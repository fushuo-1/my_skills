/**
 * @file sensor_driver_template.c
 * @brief 传感器驱动模板文件
 * @description 这是一个符合嵌入式C代码规范的传感器驱动模板，
 *              采用面向对象思想进行封装，参考OpenMV和Linux内核驱动风格
 */

#include <stdint.h>
#include <stdbool.h>

/* ==================== 宏定义 ==================== */

#define SENSOR_I2C_ADDR        0x30    // 传感器I2C地址
#define SENSOR_REG_ID          0x00    // ID寄存器地址
#define SENSOR_REG_CTRL        0x01    // 控制寄存器地址
#define SENSOR_REG_DATA        0x02    // 数据寄存器地址
#define I2C_TIMEOUT_MS         100     // I2C超时时间（毫秒）
#define MAX_RETRY_COUNT        3       // 最大重试次数

/* ==================== 类型定义 ==================== */

/**
 * @brief 传感器状态枚举
 */
typedef enum {
    SENSOR_STATUS_OK = 0,      // 正常
    SENSOR_STATUS_ERROR,       // 错误
    SENSOR_STATUS_TIMEOUT,     // 超时
    SENSOR_STATUS_BUSY         // 忙碌
} sensor_status_t;

/**
 * @brief 传感器配置结构体
 */
typedef struct {
    uint8_t sample_rate;       // 采样率
    uint8_t resolution;        // 分辨率
    bool enable_interrupt;    // 是否使能中断
} sensor_config_t;

/**
 * @brief 传感器结构体（面向对象封装）
 */
typedef struct {
    uint8_t slv_addr;          // 从设备地址
    
    // 函数指针成员
    void (*reset)(void);
    sensor_status_t (*read_reg)(uint8_t reg, uint8_t *data);
    sensor_status_t (*write_reg)(uint8_t reg, uint8_t data);
    sensor_status_t (*set_config)(sensor_config_t *config);
    sensor_status_t (*get_data)(uint16_t *data);
    
    // 私有成员
    sensor_config_t config;    // 当前配置
    bool is_initialized;      // 初始化标志
} sensor_t;

/* ==================== 静态函数声明 ==================== */

static void sensor_reset(void);
static sensor_status_t sensor_read_reg(uint8_t reg, uint8_t *data);
static sensor_status_t sensor_write_reg(uint8_t reg, uint8_t data);
static sensor_status_t sensor_set_config(sensor_config_t *config);
static sensor_status_t sensor_get_data(uint16_t *data);

/* ==================== 静态函数实现 ==================== */

/**
 * @brief 传感器复位函数
 * @note   通过写控制寄存器实现软复位
 */
static void sensor_reset(void) {
    uint8_t reset_cmd = 0x01;
    sensor_write_reg(SENSOR_REG_CTRL, reset_cmd);
}

/**
 * @brief 读取传感器寄存器
 * @param reg  寄存器地址
 * @param data 读取的数据指针
 * @return 传感器状态
 */
static sensor_status_t sensor_read_reg(uint8_t reg, uint8_t *data) {
    // I2C读取实现
    // 这里省略具体的I2C读取代码
    *data = 0;
    return SENSOR_STATUS_OK;
}

/**
 * @brief 写入传感器寄存器
 * @param reg  寄存器地址
 * @param data 要写入的数据
 * @return 传感器状态
 */
static sensor_status_t sensor_write_reg(uint8_t reg, uint8_t data) {
    // I2C写入实现
    // 这里省略具体的I2C写入代码
    return SENSOR_STATUS_OK;
}

/**
 * @brief 设置传感器配置
 * @param config 配置结构体指针
 * @return 传感器状态
 */
static sensor_status_t sensor_set_config(sensor_config_t *config) {
    sensor_status_t status;
    
    // 写入采样率配置
    status = sensor_write_reg(SENSOR_REG_CTRL, config->sample_rate);
    if (status != SENSOR_STATUS_OK) {
        return status;
    }
    
    // 写入分辨率配置
    status = sensor_write_reg(SENSOR_REG_CTRL + 1, config->resolution);
    if (status != SENSOR_STATUS_OK) {
        return status;
    }
    
    return SENSOR_STATUS_OK;
}

/**
 * @brief 获取传感器数据
 * @param data 数据指针
 * @return 传感器状态
 */
static sensor_status_t sensor_get_data(uint16_t *data) {
    uint8_t low_byte, high_byte;
    sensor_status_t status;
    
    // 读取低字节
    status = sensor_read_reg(SENSOR_REG_DATA, &low_byte);
    if (status != SENSOR_STATUS_OK) {
        return status;
    }
    
    // 读取高字节
    status = sensor_read_reg(SENSOR_REG_DATA + 1, &high_byte);
    if (status != SENSOR_STATUS_OK) {
        return status;
    }
    
    // 组合数据
    *data = (uint16_t)high_byte << 8 | low_byte;
    
    return SENSOR_STATUS_OK;
}

/* ==================== 公共函数实现 ==================== */

/**
 * @brief 传感器初始化函数
 * @param sensor 传感器结构体指针
 * @return 初始化状态，0表示成功，非0表示失败
 */
uint8_t sensor_init(sensor_t *sensor) {
    // 检查指针有效性
    if (sensor == NULL) {
        return 1;
    }
    
    // 设置从设备地址
    sensor->slv_addr = SENSOR_I2C_ADDR;
    
    // 绑定函数指针（面向对象核心）
    sensor->reset = sensor_reset;
    sensor->read_reg = sensor_read_reg;
    sensor->write_reg = sensor_write_reg;
    sensor->set_config = sensor_set_config;
    sensor->get_data = sensor_get_data;
    
    // 初始化默认配置
    sensor->config.sample_rate = 10;
    sensor->config.resolution = 12;
    sensor->config.enable_interrupt = false;
    
    // 执行复位
    sensor->reset();
    
    // 设置初始化标志
    sensor->is_initialized = true;
    
    return 0;
}

/**
 * @brief 传感器去初始化函数
 * @param sensor 传感器结构体指针
 * @return 去初始化状态，0表示成功，非0表示失败
 */
uint8_t sensor_deinit(sensor_t *sensor) {
    // 检查指针有效性
    if (sensor == NULL) {
        return 1;
    }
    
    // 清除初始化标志
    sensor->is_initialized = false;
    
    // 清空函数指针
    sensor->reset = NULL;
    sensor->read_reg = NULL;
    sensor->write_reg = NULL;
    sensor->set_config = NULL;
    sensor->get_data = NULL;
    
    return 0;
}

/* ==================== 使用示例 ==================== */

/*
 * 使用示例：
 * 
 * int main(void) {
 *     sensor_t my_sensor;
 *     uint16_t sensor_data;
 *     sensor_config_t config;
 *     
 *     // 初始化传感器
 *     if (sensor_init(&my_sensor) != 0) {
 *         // 初始化失败处理
 *         return -1;
 *     }
 *     
 *     // 配置传感器
 *     config.sample_rate = 20;
 *     config.resolution = 16;
 *     config.enable_interrupt = true;
 *     my_sensor.set_config(&config);
 *     
 *     // 读取数据
 *     if (my_sensor.get_data(&sensor_data) == SENSOR_STATUS_OK) {
 *         // 处理数据
 *     }
 *     
 *     // 去初始化
 *     sensor_deinit(&my_sensor);
 *     
 *     return 0;
 * }
 */
