import service, { requestWithRetry } from './index'

/**
 * Bắt đầu tạo báo cáo
 * @param {Object} data - { simulation_id, force_regenerate? }
 */
export const generateReport = (data) => {
  return requestWithRetry(() => service.post('/api/report/generate', data), 3, 1000)
}

/**
 * Lấy trạng thái tạo báo cáo
 * @param {string} reportId
 */
export const getReportStatus = (reportId) => {
  return service.get(`/api/report/generate/status`, { params: { report_id: reportId } })
}

/**
 * Lấy nhật ký Agent (tăng dần)
 * @param {string} reportId
 * @param {number} fromLine - Bắt đầu lấy từ dòng nào
 */
export const getAgentLog = (reportId, fromLine = 0) => {
  return service.get(`/api/report/${reportId}/agent-log`, { params: { from_line: fromLine } })
}

/**
 * Lấy nhật ký bảng điều khiển (tăng dần)
 * @param {string} reportId
 * @param {number} fromLine - Bắt đầu lấy từ dòng nào
 */
export const getConsoleLog = (reportId, fromLine = 0) => {
  return service.get(`/api/report/${reportId}/console-log`, { params: { from_line: fromLine } })
}

/**
 * Lấy chi tiết báo cáo
 * @param {string} reportId
 */
export const getReport = (reportId) => {
  return service.get(`/api/report/${reportId}`)
}

/**
 * Trò chuyện với Report Agent
 * @param {Object} data - { simulation_id, message, chat_history? }
 */
export const chatWithReport = (data) => {
  return requestWithRetry(() => service.post('/api/report/chat', data), 3, 1000)
}
