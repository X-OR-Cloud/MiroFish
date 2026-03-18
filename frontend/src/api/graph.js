import service, { requestWithRetry } from './index'

/**
 * Tạo ontology (tải lên tài liệu và yêu cầu mô phỏng)
 * @param {Object} data - Bao gồm files, simulation_requirement, project_name, v.v.
 * @returns {Promise}
 */
export function generateOntology(formData) {
  return requestWithRetry(() => 
    service({
      url: '/api/graph/ontology/generate',
      method: 'post',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  )
}

/**
 * Xây dựng đồ thị
 * @param {Object} data - Bao gồm project_id, graph_name, v.v.
 * @returns {Promise}
 */
export function buildGraph(data) {
  return requestWithRetry(() =>
    service({
      url: '/api/graph/build',
      method: 'post',
      data
    })
  )
}

/**
 * Truy vấn trạng thái tác vụ
 * @param {String} taskId - ID tác vụ
 * @returns {Promise}
 */
export function getTaskStatus(taskId) {
  return service({
    url: `/api/graph/task/${taskId}`,
    method: 'get'
  })
}

/**
 * Lấy dữ liệu đồ thị
 * @param {String} graphId - ID đồ thị
 * @returns {Promise}
 */
export function getGraphData(graphId) {
  return service({
    url: `/api/graph/data/${graphId}`,
    method: 'get'
  })
}

/**
 * Lấy thông tin dự án
 * @param {String} projectId - ID dự án
 * @returns {Promise}
 */
export function getProject(projectId) {
  return service({
    url: `/api/graph/project/${projectId}`,
    method: 'get'
  })
}
