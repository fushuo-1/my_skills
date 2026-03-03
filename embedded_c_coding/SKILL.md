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

#### 函数指针类型命名
- **规则**：对象名 + 动词短语 + `_fn` 后缀
- **示例**：
  ```c
  typedef error_t (*motor_init_fn)(motor_t *motor, uint32_t param);
  typedef error_t (*motor_start_fn)(motor_t *motor, uint16_t speed);
  typedef error_t (*motor_stop_fn)(motor_t *motor);
  typedef void (*motor_callback_fn)(motor_t *motor, uint8_t event);
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

### 3. 面向对象函数指针封装规范（重点）

采用结构体自包含设计，将数据成员与操作函数指针统一封装，实现 C 语言的面向对象编程。

#### 3.1 前向声明
在定义函数指针类型之前，先进行结构体的前向声明：
```c
/* === 前向声明 === */
typedef struct motor_t motor_t;
```

#### 3.2 函数指针类型定义
为每个操作方法定义独立的函数指针类型，遵循 `对象名_动词_fn` 命名规范：
```c
/* === 函数指针类型定义 === */

/**
 * @brief 初始化函数指针类型
 */
typedef motor_error_t (*motor_init_fn)(motor_t *motor, uint32_t config);

/**
 * @brief 启动函数指针类型
 */
typedef motor_error_t (*motor_start_fn)(motor_t *motor, uint16_t speed);

/**
 * @brief 停止函数指针类型
 */
typedef motor_error_t (*motor_stop_fn)(motor_t *motor);

/**
 * @brief 设置速度函数指针类型
 */
typedef motor_error_t (*motor_set_speed_fn)(motor_t *motor, uint16_t speed);

/**
 * @brief 获取状态函数指针类型
 */
typedef motor_state_t (*motor_get_state_fn)(motor_t *motor);

/**
 * @brief 定时器中断处理函数指针类型
 */
typedef void (*motor_timer_isr_fn)(motor_t *motor);
```

#### 3.3 结构体自包含设计
结构体包含硬件配置、运行状态和函数指针成员：
```c
/**
 * @brief 电机控制器结构体
 * @note  采用面向对象思想封装，包含硬件配置、运行状态和操作方法
 */
struct motor_t {
    /* 硬件配置 */
    TIM_HandleTypeDef *pwm_timer;      /**< PWM定时器指针 */
    TIM_HandleTypeDef *comm_timer;     /**< 通信定时器指针 */

    /* 运行状态 */
    motor_state_t state;               /**< 电机运行状态 */
    motor_direction_t direction;       /**< 旋转方向 */
    uint8_t current_step;              /**< 当前步骤 */

    /* 控制参数 */
    uint16_t duty_cycle;               /**< 当前占空比 */
    uint32_t control_interval_us;      /**< 控制间隔 (微秒) */

    /* 函数指针 - 操作方法 */
    motor_init_fn           init;           /**< 初始化函数 */
    motor_start_fn          start;          /**< 启动函数 */
    motor_stop_fn           stop;           /**< 停止函数 */
    motor_set_speed_fn      set_speed;      /**< 设置速度 */
    motor_get_state_fn      get_state;      /**< 获取状态 */
    motor_timer_isr_fn      timer_isr;      /**< 定时器中断处理 */

    /* 函数指针 - 回调函数 */
    void (*on_complete)(uint8_t step);   /**< 操作完成回调 */
    void (*on_error)(uint32_t error_code); /**< 错误回调 */
};
```

#### 3.4 函数指针绑定规范
初始化函数负责绑定所有函数指针：
```c
/**
 * @brief  电机驱动初始化函数（函数指针绑定核心）
 * @param  motor: 电机控制器结构体指针
 * @param  pwm_timer: PWM定时器指针
 * @retval 错误码
 * @note   这是驱动的入口点，完成所有函数指针绑定
 */
motor_error_t bsp_motor_init(motor_t *motor, TIM_HandleTypeDef *pwm_timer) {
    if (motor == NULL || pwm_timer == NULL) {
        return MOTOR_ERROR_NULL_PTR;
    }

    /* 绑定硬件配置 */
    motor->pwm_timer = pwm_timer;
    motor->state = MOTOR_STATE_IDLE;

    /* 绑定操作方法函数指针 */
    motor->init       = motor_impl_init;
    motor->start      = motor_impl_start;
    motor->stop       = motor_impl_stop;
    motor->set_speed  = motor_impl_set_speed;
    motor->get_state  = motor_impl_get_state;
    motor->timer_isr  = motor_impl_timer_isr;

    return MOTOR_OK;
}
```

#### 3.5 函数指针实现规范
- 实现函数使用 `static` 修饰，仅在模块内部可见
- 命名格式：`对象名_impl_动词`（impl 表示 implementation）
- 所有函数指针第一个参数必须是结构体自身指针
```c
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

    motor->state = MOTOR_STATE_RUNNING;
    motor->duty_cycle = speed;

    /* 硬件操作 */
    __HAL_TIM_SET_COMPARE(motor->pwm_timer, TIM_CHANNEL_1, speed);

    return MOTOR_OK;
}
```

### 4. 代码注释规范

- **语言**：所有注释必须使用中文
- **位置**：函数头部、复杂逻辑、关键参数说明
- **Doxygen 格式**：使用标准 Doxygen 注释格式
- **示例**：
  ```c
  /**
   * @brief  电机初始化函数
   * @param  motor 电机结构体指针
   * @param  config 配置参数
   * @retval 错误码，MOTOR_OK表示成功
   * @note   调用此函数前需确保硬件时钟已使能
   */
  motor_error_t bsp_motor_init(motor_t *motor, uint32_t config);
  ```

## 完整代码模板示例

### 头文件模板 (.h)

```c
/**
 ******************************************************************************
 * @file    motor_driver.h
 * @brief   电机驱动头文件
 * @author  Project
 * @date    2026
 ******************************************************************************
 * @attention
 * 采用面向对象思想封装，支持函数指针绑定模式
 ******************************************************************************
 */

#ifndef __MOTOR_DRIVER_H
#define __MOTOR_DRIVER_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/

#include "main.h"

/* Exported types ------------------------------------------------------------*/

/**
 * @brief 电机错误码枚举
 */
typedef enum {
    MOTOR_OK = 0,                  /**< 成功 */
    MOTOR_ERROR_NULL_PTR,          /**< 空指针错误 */
    MOTOR_ERROR_INVALID_PARAM,     /**< 无效参数 */
    MOTOR_ERROR_TIMER              /**< 定时器错误 */
} motor_error_t;

/**
 * @brief 电机运行状态枚举
 */
typedef enum {
    MOTOR_STATE_IDLE = 0,          /**< 空闲状态 */
    MOTOR_STATE_RUNNING,           /**< 运行中 */
    MOTOR_STATE_ERROR              /**< 错误状态 */
} motor_state_t;

/* === 前向声明 === */

typedef struct motor_t motor_t;

/* === 函数指针类型定义 === */

/**
 * @brief 初始化函数指针类型
 */
typedef motor_error_t (*motor_init_fn)(motor_t *motor, TIM_HandleTypeDef *timer);

/**
 * @brief 启动函数指针类型
 */
typedef motor_error_t (*motor_start_fn)(motor_t *motor, uint16_t speed);

/**
 * @brief 停止函数指针类型
 */
typedef motor_error_t (*motor_stop_fn)(motor_t *motor);

/**
 * @brief 获取状态函数指针类型
 */
typedef motor_state_t (*motor_get_state_fn)(motor_t *motor);

/**
 * @brief 电机控制器结构体
 * @note  采用面向对象思想封装
 */
struct motor_t {
    /* 硬件配置 */
    TIM_HandleTypeDef *pwm_timer;   /**< PWM定时器指针 */

    /* 运行状态 */
    motor_state_t state;            /**< 电机运行状态 */
    uint16_t duty_cycle;            /**< 当前占空比 */

    /* 函数指针 - 操作方法 */
    motor_init_fn      init;        /**< 初始化函数 */
    motor_start_fn     start;       /**< 启动函数 */
    motor_stop_fn      stop;        /**< 停止函数 */
    motor_get_state_fn get_state;   /**< 获取状态 */

    /* 函数指针 - 回调函数 */
    void (*on_error)(uint32_t error_code); /**< 错误回调 */
};

/* Exported functions prototypes ---------------------------------------------*/

/**
 * @brief  电机驱动初始化函数（函数指针绑定核心）
 * @param  motor: 电机控制器结构体指针
 * @param  timer: PWM定时器指针
 * @retval 错误码
 */
motor_error_t bsp_motor_init(motor_t *motor, TIM_HandleTypeDef *timer);

#ifdef __cplusplus
}
#endif

#endif /* __MOTOR_DRIVER_H */
```

### 源文件模板 (.c)

```c
/**
 ******************************************************************************
 * @file    motor_driver.c
 * @brief   电机驱动实现文件
 ******************************************************************************
 */

#include "motor_driver.h"

/* Private function prototypes -----------------------------------------------*/

static motor_error_t motor_impl_init(motor_t *motor, TIM_HandleTypeDef *timer);
static motor_error_t motor_impl_start(motor_t *motor, uint16_t speed);
static motor_error_t motor_impl_stop(motor_t *motor);
static motor_state_t motor_impl_get_state(motor_t *motor);

/* Private functions ---------------------------------------------------------*/

/**
 * @brief 电机初始化实现函数
 * @param motor 电机结构体指针
 * @param timer PWM定时器指针
 * @return 错误码
 */
static motor_error_t motor_impl_init(motor_t *motor, TIM_HandleTypeDef *timer) {
    if (motor == NULL || timer == NULL) {
        return MOTOR_ERROR_NULL_PTR;
    }

    motor->pwm_timer = timer;
    motor->state = MOTOR_STATE_IDLE;
    motor->duty_cycle = 0;

    /* 启动PWM */
    HAL_TIM_PWM_Start(timer, TIM_CHANNEL_1);

    return MOTOR_OK;
}

/**
 * @brief 电机启动实现函数
 * @param motor 电机结构体指针
 * @param speed 启动速度 (0-1000)
 * @return 错误码
 */
static motor_error_t motor_impl_start(motor_t *motor, uint16_t speed) {
    if (motor == NULL) {
        return MOTOR_ERROR_NULL_PTR;
    }

    motor->state = MOTOR_STATE_RUNNING;
    motor->duty_cycle = speed;

    __HAL_TIM_SET_COMPARE(motor->pwm_timer, TIM_CHANNEL_1, speed);

    return MOTOR_OK;
}

/**
 * @brief 电机停止实现函数
 * @param motor 电机结构体指针
 * @return 错误码
 */
static motor_error_t motor_impl_stop(motor_t *motor) {
    if (motor == NULL) {
        return MOTOR_ERROR_NULL_PTR;
    }

    motor->state = MOTOR_STATE_IDLE;
    motor->duty_cycle = 0;

    __HAL_TIM_SET_COMPARE(motor->pwm_timer, TIM_CHANNEL_1, 0);

    return MOTOR_OK;
}

/**
 * @brief 获取电机状态实现函数
 * @param motor 电机结构体指针
 * @return 电机运行状态
 */
static motor_state_t motor_impl_get_state(motor_t *motor) {
    if (motor == NULL) {
        return MOTOR_STATE_ERROR;
    }
    return motor->state;
}

/* Exported functions --------------------------------------------------------*/

/**
 * @brief  电机驱动初始化函数（函数指针绑定核心）
 * @param  motor: 电机控制器结构体指针
 * @param  timer: PWM定时器指针
 * @retval 错误码
 * @note   这是驱动的入口点，完成所有函数指针绑定
 */
motor_error_t bsp_motor_init(motor_t *motor, TIM_HandleTypeDef *timer) {
    if (motor == NULL || timer == NULL) {
        return MOTOR_ERROR_NULL_PTR;
    }

    /* 绑定硬件配置 */
    motor->pwm_timer = timer;
    motor->state = MOTOR_STATE_IDLE;

    /* 绑定操作方法函数指针 */
    motor->init      = motor_impl_init;
    motor->start     = motor_impl_start;
    motor->stop      = motor_impl_stop;
    motor->get_state = motor_impl_get_state;

    /* 执行初始化 */
    return motor->init(motor, timer);
}
```

## 代码检查清单

在生成代码时，必须检查以下项目：

- [ ] 变量命名是否使用小写字母 + 下划线
- [ ] 函数命名是否遵循"对象名 + 动词短语"格式
- [ ] 类型/结构体命名是否以 `_t` 结尾
- [ ] 函数指针类型命名是否使用 `*_fn` 后缀
- [ ] 宏与常量是否使用全大写字母 + 下划线
- [ ] 所有注释是否使用中文
- [ ] 函数是否有完整的中文 Doxygen 注释
- [ ] 是否进行了前向声明
- [ ] 结构体是否包含函数指针成员
- [ ] 函数指针第一个参数是否为结构体自身指针
- [ ] 初始化函数是否正确绑定所有函数指针
- [ ] 实现函数是否使用 `static` 修饰
- [ ] 代码是否符合嵌入式开发规范（紧凑、高效）

## 使用说明

当用户请求编写嵌入式 C 代码时，特别是硬件驱动相关代码，请：

1. 严格按照上述命名规范编写代码
2. 使用前向声明和函数指针类型定义
3. 结构体采用自包含设计（数据 + 函数指针）
4. 确保所有注释使用中文 Doxygen 格式
5. 初始化函数完成所有函数指针绑定
6. 在代码生成后，对照检查清单进行验证

## 参考资源

- OpenMV 驱动代码风格
- Linux 内核驱动编程规范
- MISRA C 编码规范（嵌入式安全相关）
- STM32 HAL 库代码风格
