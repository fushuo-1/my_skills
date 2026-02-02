---
name: embedded-c-coding
description: 嵌入式 C 代码编写规范，包括硬件驱动、传感器外设封装、FOC 电机控制等。使用面向对象思想进行 C 语言封装，遵循统一命名约定和中文注释规范。当用户请求编写嵌入式 C 代码、硬件驱动、传感器驱动、FOC 电机控制代码或嵌入式系统底层代码时使用此 Skill。
---

# 嵌入式 C 代码编写规范 Skill

## Skill 描述

这是一个专门用于嵌入式 C 语言代码编写的 Claude Skill，确保生成的代码符合嵌入式开发规范，采用面向对象的设计思想，并遵循统一的命名约定。

## 适用场景

- 嵌入式硬件驱动编写
- 传感器/外设驱动封装
- 硬件接口抽象层设计
- FOC 电机控制相关代码
- 其他嵌入式系统底层代码

## 核心规范

### 1. 命名规范

#### 变量命名
- **规则**：小写字母 + 下划线
- **示例**：
  ```c
  uint8_t motor_speed;
  float current_value;
  int16_t adc_result;
  ```

#### 函数命名
- **规则**：对象名 + 动词短语，体现面向对象思想
- **示例**：
  ```c
  motor_init();           // 电机初始化
  motor_set_speed();      // 设置电机速度
  sensor_read_reg();      // 读取传感器寄存器
  driver_write_reg();     // 驱动写寄存器
  ```

#### 类型与结构体命名
- **规则**：小写英文，类型通常以 `_t` 结尾
- **示例**：
  ```c
  typedef struct {
      uint8_t slv_addr;
      void (*reset)(void);
      void (*read_reg)(uint8_t reg, uint8_t *data);
      void (*write_reg)(uint8_t reg, uint8_t data);
  } sensor_t;
  
  typedef struct {
      float kp;
      float ki;
      float kd;
  } pid_param_t;
  ```

#### 宏与常量命名
- **规则**：全大写字母 + 下划线
- **示例**：
  ```c
  #define MAX_SPEED 10000
  #define I2C_TIMEOUT 1000
  #define PWM_FREQUENCY 20000
  ```

### 2. 代码注释规范

- **语言**：所有注释必须使用中文
- **位置**：函数头部、复杂逻辑、关键参数说明
- **示例**：
  ```c
  /**
   * @brief 电机初始化函数
   * @param motor 电机结构体指针
   * @return 初始化状态，0表示成功，非0表示失败
   */
  int motor_init(motor_t *motor) {
      // 初始化电机参数
      motor->speed = 0;
      return 0;
  }
  ```

### 3. 硬件接口抽象封装规范

参考 OpenMV 或 Linux 内核驱动风格，采用面向对象思想进行 C 语言封装。

#### 结构体定义要求
- 必须包含硬件地址成员（如 `slv_addr`）
- 必须包含控制功能的函数指针成员
- 接口清晰、易于扩展

#### 初始化函数要求
- 函数名格式：`[对象名]_init`
- 参数：接受结构体指针作为参数
- 核心逻辑：将本地实现的静态功能函数一一赋值给结构体对应的函数指针成员

#### 代码风格要求
- 使用面向对象的思想进行 C 语言封装
- 确保接口清晰、易于扩展
- 代码紧凑且符合嵌入式开发规范

## 代码模板示例

### 硬件驱动初始化模板

```c
/**
 * @brief 传感器复位函数（静态内部函数）
 */
static void sensor_reset(void) {
    // 复位逻辑
}

/**
 * @brief 读取传感器寄存器（静态内部函数）
 * @param reg 寄存器地址
 * @param data 读取的数据指针
 */
static void sensor_read_reg(uint8_t reg, uint8_t *data) {
    // 读取寄存器逻辑
}

/**
 * @brief 写入传感器寄存器（静态内部函数）
 * @param reg 寄存器地址
 * @param data 要写入的数据
 */
static void sensor_write_reg(uint8_t reg, uint8_t data) {
    // 写入寄存器逻辑
}

/**
 * @brief 传感器初始化函数
 * @param sensor 传感器结构体指针
 * @return 初始化状态，0表示成功，非0表示失败
 */
int sensor_init(sensor_t *sensor) {
    // 绑定函数指针
    sensor->reset = sensor_reset;
    sensor->read_reg = sensor_read_reg;
    sensor->write_reg = sensor_write_reg;
    
    // 其他初始化逻辑
    return 0;
}
```

## 代码检查清单

在生成代码时，必须检查以下项目：

- [ ] 变量命名是否使用小写字母 + 下划线
- [ ] 函数命名是否遵循"对象名 + 动词短语"格式
- [ ] 类型/结构体命名是否以 `_t` 结尾
- [ ] 宏与常量是否使用全大写字母 + 下划线
- [ ] 所有注释是否使用中文
- [ ] 函数是否有完整的中文注释说明
- [ ] 硬件驱动是否采用面向对象封装
- [ ] 初始化函数是否正确绑定函数指针
- [ ] 代码是否符合嵌入式开发规范（紧凑、高效）

## 使用说明

当用户请求编写嵌入式 C 代码时，特别是硬件驱动相关代码，请：

1. 严格按照上述命名规范编写代码
2. 参考提供的代码模板
3. 确保所有注释使用中文
4. 采用面向对象思想进行封装
5. 在代码生成后，对照检查清单进行验证

## 参考资源

- OpenMV 驱动代码风格
- Linux 内核驱动编程规范
- MISRA C 编码规范（嵌入式安全相关）
