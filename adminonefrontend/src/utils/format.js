/**
 * 格式化日期时间
 * @param {string|Date} date - 要格式化的日期
 * @param {boolean} [withTime=true] - 是否包含时间
 * @returns {string} 格式化后的日期时间字符串
 */
export const formatDate = (date, withTime = true) => {
  if (!date) return '-'
  
  const d = new Date(date)
  if (isNaN(d.getTime())) return '-'

  const options = {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }

  if (withTime) {
    options.hour = '2-digit'
    options.minute = '2-digit'
  }

  return d.toLocaleString('zh-CN', options)
}

/**
 * 格式化文件大小
 * @param {number} bytes - 字节数
 * @returns {string} 格式化后的文件大小
 */
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}

/**
 * 格式化金额
 * @param {number} amount - 金额
 * @param {string} [currency='¥'] - 货币符号
 * @returns {string} 格式化后的金额
 */
export const formatMoney = (amount, currency = '¥') => {
  if (typeof amount !== 'number') return '-'
  return `${currency}${amount.toFixed(2)}`
}

/**
 * 格式化流量
 * @param {number} bytes - 字节数
 * @returns {string} 格式化后的流量
 */
export const formatTraffic = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
} 