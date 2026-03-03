# 嵌入式 C 代码检查清单

## 使用说明

本检查清单用于验证生成的嵌入式 C 代码是否符合项目规范。在代码生成完成后，请逐项检查以下内容。

---

## 一、命名规范检查

### 1.1 变量命名
- [ ] 所有变量名使用小写字母 + 下划线格式
- [ ] 变量名具有描述性，能清晰表达其用途
- [ ] 避免使用单字母变量名（循环变量除外）
- [ ] 布尔变量使用 `is_`、`has_`、`can_` 等前缀

**示例检查：**
```c
// ✅ 正确
uint8_t motor_speed;
float current_value;
bool is_initialized;

// ❌ 错误
uint8_t MotorSpeed;      // 大写字母
float currentValue;      // 驼峰命名
bool initialized;       // 布尔变量缺少前缀
```

### 1.2 函数命名
- [ ] 函数名格式：对象名 + 动词短语
- [ ] 函数名清晰表达其功能
- [ ] 初始化函数使用 `_init` 后缀
- [ ] 去初始化函数使用 `_deinit` 后缀
- [ ] 获取数据函数使用 `get_` 前缀
- [ ] 设置数据函数使用 `set_` 前缀

**示例检查：**
```c
// ✅ 正确
motor_init();
motor_set_speed();
sensor_read_reg();
driver_write_reg();

// ❌ 错误
MotorInit();             // 大写字母
initMotor();             // 动词在前
readSensorReg();         // 驼峰命名
```

### 1.3 类型与结构体命名
- [ ] 类型名使用小写英文
- [ ] 类型名以 `_t` 结尾
- [ ] 结构体名使用小写英文 + `_t` 后缀
- [ ] 枚举名使用小写英文 + `_t` 后缀

**示例检查：**
```c
// ✅ 正确
typedef struct {
    uint8_t addr;
} sensor_t;

typedef enum {
    STATUS_OK,
    STATUS_ERROR
} status_t;

// ❌ 错误
typedef struct {
    uint8_t addr;
} Sensor;               // 缺少 _t 后缀

typedef enum {
    STATUS_OK,
    STATUS_ERROR
} Status;               // 缺少 _t 后缀
```

### 1.4 函数指针类型命名
- [ ] 函数指针类型名使用 `对象名_动词_fn` 格式
- [ ] 函数指针类型以 `_fn` 后缀结尾
- [ ] 函数指针第一个参数为结构体自身指针

**示例检查：**
```c
// ✅ 正确
typedef motor_error_t (*motor_init_fn)(motor_t *motor, uint32_t config);
typedef motor_error_t (*motor_start_fn)(motor_t *motor, uint16_t speed);
typedef void (*motor_callback_fn)(motor_t *motor, uint8_t event);

// ❌ 错误
typedef motor_error_t (*MotorInit)(motor_t *motor);    // 大写字母，缺少 _fn 后缀
typedef motor_error_t (*motor_init)(motor_t *motor);   // 缺少 _fn 后缀
typedef motor_error_t (*motor_init_fn)(uint32_t config); // 缺少 self 指针参数
```

### 1.4 宏与常量命名
- [ ] 宏名使用全大写字母 + 下划线
- [ ] 常量名使用全大写字母 + 下划线
- [ ] 宏定义有清晰的注释说明

**示例检查：**
```c
// ✅ 正确
#define MAX_SPEED 10000
#define I2C_TIMEOUT_MS 100
#define PWM_FREQUENCY 20000

// ❌ 错误
#define MaxSpeed 10000       // 大小写混合
#define i2c_timeout 100      // 小写
```

---

## 二、注释规范检查

### 2.1 注释语言
- [ ] 所有注释使用中文
- [ ] 注释内容清晰、准确
- [ ] 避免使用拼音或中英文混合

### 2.2 文件头注释
- [ ] 每个源文件包含文件头注释
- [ ] 包含 `@file` 文件名
- [ ] 包含 `@brief` 简要描述
- [ ] 包含 `@description` 详细描述（可选）

**示例检查：**
```c
/**
 * @file motor_driver.c
 * @brief 电机驱动实现文件
 * @description 实现FOC电机控制的核心功能，包括PWM输出、电流采样等
 */
```

### 2.3 函数注释
- [ ] 每个公共函数都有完整注释
- [ ] 包含 `@brief` 功能描述
- [ ] 包含 `@param` 参数说明
- [ ] 包含 `@return` 返回值说明
- [ ] 复杂函数包含 `@note` 注意事项

**示例检查：**
```c
/**
 * @brief 电机初始化函数
 * @param motor 电机结构体指针
 * @return 初始化状态，0表示成功，非0表示失败
 * @note 调用此函数前需确保硬件已正确配置
 */
int motor_init(motor_t *motor);
```

### 2.4 代码内注释
- [ ] 复杂逻辑有注释说明
- [ ] 关键算法有注释说明
- [ ] 魔法数字有注释说明
- [ ] 注释与代码同步更新

---

## 三、面向对象函数指针封装检查

### 3.1 前向声明
- [ ] 结构体定义前有前向声明
- [ ] 前向声明格式正确：`typedef struct xxx_t xxx_t;`

**示例检查：**
```c
// ✅ 正确
typedef struct motor_t motor_t;  // 前向声明

typedef motor_error_t (*motor_init_fn)(motor_t *motor);  // 函数指针定义

struct motor_t {                // 结构体定义
    // ...
};
```

### 3.2 函数指针类型定义
- [ ] 每个操作方法有独立的函数指针类型定义
- [ ] 函数指针类型命名使用 `*_fn` 后缀
- [ ] 函数指针第一个参数为结构体自身指针
- [ ] 函数指针有完整的中文注释

**示例检查：**
```c
// ✅ 正确
/**
 * @brief 初始化函数指针类型
 */
typedef motor_error_t (*motor_init_fn)(motor_t *motor, uint32_t config);

/**
 * @brief 启动函数指针类型
 */
typedef motor_error_t (*motor_start_fn)(motor_t *motor, uint16_t speed);
```

### 3.3 结构体自包含设计
- [ ] 结构体包含硬件配置成员
- [ ] 结构体包含运行状态成员
- [ ] 结构体包含函数指针成员（操作方法）
- [ ] 结构体包含回调函数指针（可选）
- [ ] 函数指针成员有完整的中文注释

**示例检查：**
```c
// ✅ 正确
struct motor_t {
    /* 硬件配置 */
    TIM_HandleTypeDef *pwm_timer;      /**< PWM定时器指针 */

    /* 运行状态 */
    motor_state_t state;               /**< 电机运行状态 */
    uint16_t duty_cycle;               /**< 当前占空比 */

    /* 函数指针 - 操作方法 */
    motor_init_fn      init;           /**< 初始化函数 */
    motor_start_fn     start;          /**< 启动函数 */
    motor_stop_fn      stop;           /**< 停止函数 */

    /* 函数指针 - 回调函数 */
    void (*on_error)(uint32_t code);   /**< 错误回调 */
};
```

### 3.4 函数指针绑定
- [ ] 有专门的初始化函数负责绑定函数指针
- [ ] 初始化函数命名格式：`bsp_[对象名]_init`
- [ ] 所有函数指针都被正确绑定
- [ ] 绑定前检查指针有效性

**示例检查：**
```c
// ✅ 正确
motor_error_t bsp_motor_init(motor_t *motor, TIM_HandleTypeDef *timer) {
    if (motor == NULL || timer == NULL) {
        return MOTOR_ERROR_NULL_PTR;
    }

    /* 绑定硬件配置 */
    motor->pwm_timer = timer;

    /* 绑定操作方法函数指针 */
    motor->init  = motor_impl_init;
    motor->start = motor_impl_start;
    motor->stop  = motor_impl_stop;

    return MOTOR_OK;
}
```

### 3.5 实现函数规范
- [ ] 实现函数使用 `static` 修饰
- [ ] 实现函数命名格式：`对象名_impl_动词`
- [ ] 实现函数第一个参数为结构体自身指针
- [ ] 实现函数有完整的中文注释

**示例检查：**
```c
// ✅ 正确
/**
 * @brief 电机启动实现函数（静态内部函数）
 * @param motor 电机结构体指针
 * @param speed 启动速度
 * @return 错误码
 */
static motor_error_t motor_impl_start(motor_t *motor, uint16_t speed) {
    if (motor == NULL) {
        return MOTOR_ERROR_NULL_PTR;
    }
    // 实现逻辑...
    return MOTOR_OK;
}
```

---

## 四、代码质量检查

### 4.1 代码结构
- [ ] 文件结构清晰（宏定义、类型定义、函数声明、函数实现）
- [ ] 函数长度合理（一般不超过50行）
- [ ] 函数功能单一
- [ ] 避免深层嵌套（不超过3层）

### 4.2 错误处理
- [ ] 检查指针有效性
- [ ] 检查返回值
- [ ] 有合理的错误处理逻辑
- [ ] 错误码定义清晰

### 4.3 资源管理
- [ ] 有初始化函数
- [ ] 有去初始化函数
- [ ] 资源释放完整
- [ ] 避免内存泄漏

### 4.4 代码风格
- [ ] 缩进一致（使用4空格）
- [ ] 大括号位置一致
- [ ] 空行使用合理
- [ ] 代码紧凑且符合嵌入式开发规范

---

## 五、嵌入式特定检查

### 5.1 数据类型
- [ ] 使用标准类型（uint8_t、uint16_t等）
- [ ] 避免使用 int、long 等平台相关类型
- [ ] 浮点运算考虑性能影响

### 5.2 硬件相关
- [ ] 寄存器访问使用正确的类型
- [ ] 位操作使用位运算符
- [ ] 中断处理函数正确声明
- [ ] 考虑原子操作

### 5.3 性能考虑
- [ ] 避免频繁的动态内存分配
- [ ] 循环内避免重复计算
- [ ] 使用查表法替代复杂计算（如适用）
- [ ] 考虑编译器优化选项

---

## 六、检查结果记录

| 检查项 | 结果 | 备注 |
|--------|------|------|
| 命名规范 | ☐ 通过 / ☐ 不通过 | |
| 函数指针类型命名 | ☐ 通过 / ☐ 不通过 | |
| 注释规范 | ☐ 通过 / ☐ 不通过 | |
| 前向声明 | ☐ 通过 / ☐ 不通过 | |
| 结构体自包含设计 | ☐ 通过 / ☐ 不通过 | |
| 函数指针绑定 | ☐ 通过 / ☐ 不通过 | |
| 代码质量 | ☐ 通过 / ☐ 不通过 | |
| 嵌入式特定 | ☐ 通过 / ☐ 不通过 | |

---

## 七、常见问题及修正建议

### 问题1：变量命名不符合规范
**错误示例：** `uint8_t MotorSpeed;`
**修正建议：** 改为 `uint8_t motor_speed;`

### 问题2：函数命名不符合面向对象思想
**错误示例：** `void InitMotor(motor_t *motor);`
**修正建议：** 改为 `void motor_init(motor_t *motor);`

### 问题3：类型定义缺少 _t 后缀
**错误示例：** `typedef struct {...} Sensor;`
**修正建议：** 改为 `typedef struct {...} sensor_t;`

### 问题4：函数指针类型缺少 _fn 后缀
**错误示例：** `typedef error_t (*motor_init)(motor_t *motor);`
**修正建议：** 改为 `typedef error_t (*motor_init_fn)(motor_t *motor);`

### 问题5：函数指针缺少 self 参数
**错误示例：** `typedef error_t (*motor_start_fn)(uint16_t speed);`
**修正建议：** 改为 `typedef error_t (*motor_start_fn)(motor_t *motor, uint16_t speed);`

### 问题6：缺少前向声明
**错误示例：** 直接定义函数指针类型，但结构体尚未声明
**修正建议：** 在函数指针类型定义前添加 `typedef struct motor_t motor_t;`

### 问题7：注释使用英文
**错误示例：** `// Initialize motor`
**修正建议：** 改为 `// 初始化电机`

### 问题8：初始化函数未绑定所有函数指针
**错误示例：** 初始化函数中只绑定部分函数指针
**修正建议：** 确保所有函数指针成员都被正确绑定

### 问题9：实现函数未使用 static 修饰
**错误示例：** `motor_error_t motor_impl_start(motor_t *motor, uint16_t speed)`
**修正建议：** 改为 `static motor_error_t motor_impl_start(motor_t *motor, uint16_t speed)`

---

## 八、快速检查命令

如需自动化检查，可以使用以下正则表达式：

### 检查变量命名（小写+下划线）
```
^[a-z][a-z0-9_]*$
```

### 检查函数命名（对象名+动词）
```
^[a-z][a-z0-9]*_[a-z][a-z0-9_]*$
```

### 检查函数指针类型定义（_fn后缀）
```
typedef\s+\w+\s+\(\*\s*\w+_fn\s*\)\s*\(
```

### 检查类型定义（_t后缀）
```
typedef.*\s+[a-z][a-z0-9_]*_t
```

### 检查宏定义（全大写）
```
#define\s+[A-Z][A-Z0-9_]*
```

### 检查前向声明
```
typedef\s+struct\s+\w+_t\s+\w+_t\s*;
```
