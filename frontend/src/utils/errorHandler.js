// 全局错误处理工具
import { ElMessage, ElNotification } from 'element-plus'

class ErrorHandler {
  // 错误类型映射
  static errorTypes = {
    network: '网络错误',
    validation: '验证错误',
    permission: '权限错误',
    notFound: '资源不存在',
    server: '服务器错误',
    unknown: '未知错误'
  }

  // 根据错误状态码判断错误类型
  static getErrorType(error) {
    if (!error.response) return 'network'
    
    const status = error.response.status
    if (status === 400) return 'validation'
    if (status === 401 || status === 403) return 'permission'
    if (status === 404) return 'notFound'
    if (status >= 500) return 'server'
    return 'unknown'
  }

  // 获取友好的错误消息
  static getErrorMessage(error) {
    const type = this.getErrorType(error)
    
    // 优先使用后端返回的错误消息
    if (error.response?.data?.detail) {
      return error.response.data.detail
    }
    if (error.response?.data?.message) {
      return error.response.data.message
    }
    
    // 使用预定义的错误消息
    const messages = {
      network: '网络连接失败，请检查网络设置',
      validation: '数据验证失败，请检查输入内容',
      permission: '您没有权限执行此操作',
      notFound: '请求的资源不存在',
      server: '服务器错误，请稍后重试',
      unknown: '操作失败，请重试'
    }
    
    return messages[type] || error.message || '未知错误'
  }

  // 获取错误建议
  static getErrorSuggestion(error) {
    const type = this.getErrorType(error)
    
    const suggestions = {
      network: '请检查网络连接，确保后端服务正在运行',
      validation: '请检查输入的数据格式是否正确',
      permission: '请联系管理员获取相应权限',
      notFound: '请确认资源是否存在或已被删除',
      server: '服务器遇到问题，请稍后重试或联系技术支持',
      unknown: '如果问题持续存在，请联系技术支持'
    }
    
    return suggestions[type]
  }

  // 处理错误（轻量级提示）
  static handleError(error, customMessage = null) {
    const message = customMessage || this.getErrorMessage(error)
    const type = this.getErrorType(error)
    
    ElMessage({
      message,
      type: 'error',
      duration: 5000,
      showClose: true
    })
    
    // 在控制台输出详细错误信息
    console.error('[Error Handler]', {
      type,
      message,
      error
    })
  }

  // 处理错误（详细通知）
  static handleErrorWithNotification(error, title = '操作失败') {
    const message = this.getErrorMessage(error)
    const suggestion = this.getErrorSuggestion(error)
    
    ElNotification({
      title,
      message: `${message}\n\n💡 ${suggestion}`,
      type: 'error',
      duration: 8000,
      position: 'top-right'
    })
    
    console.error('[Error Handler]', {
      title,
      message,
      suggestion,
      error
    })
  }

  // 处理成功消息
  static handleSuccess(message = '操作成功', duration = 3000) {
    ElMessage({
      message,
      type: 'success',
      duration,
      showClose: true
    })
  }

  // 处理警告消息
  static handleWarning(message, duration = 4000) {
    ElMessage({
      message,
      type: 'warning',
      duration,
      showClose: true
    })
  }

  // 处理信息消息
  static handleInfo(message, duration = 3000) {
    ElMessage({
      message,
      type: 'info',
      duration,
      showClose: true
    })
  }
}

export default ErrorHandler
