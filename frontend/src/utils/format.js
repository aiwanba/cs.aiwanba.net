/**
 * 格式化数字为带千分位的字符串
 * @param {number} num - 要格式化的数字
 * @param {number} [precision=2] - 小数位数
 * @returns {string} 格式化后的字符串
 */
export const formatNumber = (num, precision = 2) => {
  if (num === undefined || num === null) return '0'
  return Number(num).toLocaleString('zh-CN', {
    minimumFractionDigits: precision,
    maximumFractionDigits: precision
  })
}

/**
 * 格式化日期时间
 * @param {string|Date} date - 要格式化的日期
 * @returns {string} 格式化后的日期字符串
 */
export const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
} 