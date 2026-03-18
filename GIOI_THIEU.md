# MiroFish — Tài Liệu Giới Thiệu Chi Tiết

> **"Engine Trí Tuệ Bầy Đàn Đơn Giản & Toàn Năng — Dự Đoán Mọi Thứ"**

---

## Mục Lục

1. [Tổng Quan Dự Án](#1-tổng-quan-dự-án)
2. [Kiến Trúc Hệ Thống](#2-kiến-trúc-hệ-thống)
3. [Quy Trình Hoạt Động (5 Bước)](#3-quy-trình-hoạt-động-5-bước)
4. [Các Thành Phần Kỹ Thuật](#4-các-thành-phần-kỹ-thuật)
5. [API Backend](#5-api-backend)
6. [Cấu Hình & Triển Khai](#6-cấu-hình--triển-khai)
7. [Công Nghệ Sử Dụng](#7-công-nghệ-sử-dụng)

---

## 1. Tổng Quan Dự Án

**MiroFish** là một engine dự đoán AI thế hệ mới dựa trên công nghệ đa tác nhân (multi-agent). Hệ thống hoạt động theo nguyên lý "sandbox kỹ thuật số": từ dữ liệu thực tế (tin tức nóng, bản thảo chính sách, tín hiệu tài chính, hay thậm chí nội dung tiểu thuyết), MiroFish tự động xây dựng một thế giới song song kỹ thuật số độ trung thực cao. Hàng nghìn tác nhân thông minh với cá tính độc lập, bộ nhớ dài hạn và logic hành vi riêng biệt tự do tương tác và trải qua quá trình tiến hóa xã hội — cho phép người dùng quan sát và dự đoán các kịch bản tương lai.

### Điểm Nổi Bật

| Khả Năng | Mô Tả |
|---|---|
| **Dự đoán dư luận** | Mô phỏng phản ứng xã hội với sự kiện mới từ tin tức, chính sách |
| **Phân tích kịch bản** | Kiểm thử chính sách, chiến lược PR trước khi triển khai thực tế |
| **Khám phá sáng tạo** | Mô phỏng kết thúc tiểu thuyết, khám phá "điều gì sẽ xảy ra nếu..." |
| **Tương tác thời gian thực** | Trò chuyện trực tiếp với bất kỳ tác nhân nào sau mô phỏng |
| **Báo cáo tự động** | Agent báo cáo tự tổng hợp và phân tích kết quả mô phỏng |

### Ứng Dụng Thực Tế Đã Được Demo

- **Mô phỏng dư luận Đại học Vũ Hán** — dự đoán phản ứng cộng đồng với một sự kiện thực
- **Dự đoán kết thúc Hồng Lâu Mộng** — phân tích từ hàng trăm nghìn từ của 80 hồi đầu

---

## 2. Kiến Trúc Hệ Thống

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND (Vue 3)                      │
│  Home → Process → Simulation → Report → Interaction         │
│         (5 bước giao diện người dùng)                       │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP / REST API
┌─────────────────────▼───────────────────────────────────────┐
│                       BACKEND (Flask)                        │
│  ┌──────────┐  ┌──────────────┐  ┌───────────┐             │
│  │ Graph API│  │Simulation API│  │ Report API│             │
│  └────┬─────┘  └──────┬───────┘  └─────┬─────┘             │
│       │               │                │                    │
│  ┌────▼───────────────▼────────────────▼──────────────────┐ │
│  │                   Services Layer                        │ │
│  │  OntologyGenerator  │  GraphBuilder  │  ProfileGenerator│ │
│  │  SimulationRunner   │  ReportAgent   │  ZepTools        │ │
│  └─────────────────────┬───────────────────────────────────┘ │
└────────────────────────┼────────────────────────────────────┘
                         │
         ┌───────────────┼──────────────────┐
         │               │                  │
    ┌────▼────┐     ┌────▼────┐      ┌─────▼─────┐
    │   LLM   │     │   Zep   │      │   OASIS   │
    │  (API)  │     │ Cloud   │      │ Engine    │
    │ GPT/Qwen│     │ (Graph  │      │(Simulation│
    │  etc.   │     │ Memory) │      │ Runner)   │
    └─────────┘     └─────────┘      └───────────┘
```

### Các Lớp Kiến Trúc

**Frontend (Vue 3 + Vite)** — Giao diện người dùng theo quy trình 5 bước tuần tự, hiển thị đồ thị tri thức bằng D3.js và theo dõi trạng thái mô phỏng theo thời gian thực.

**Backend (Flask + Python)** — Cung cấp REST API, điều phối toàn bộ quy trình từ phân tích ontology, xây dựng đồ thị, đến chạy mô phỏng và tổng hợp báo cáo.

**Zep Cloud** — Dịch vụ bộ nhớ đồ thị (Graph Memory), lưu trữ và truy vấn các thực thể, quan hệ, và bộ nhớ theo thời gian của tác nhân với cơ chế GraphRAG.

**OASIS Engine** — Framework mô phỏng mạng xã hội mã nguồn mở (CAMEL-AI), hỗ trợ mô phỏng song song trên cả hai nền tảng Twitter và Reddit.

**LLM API** — Tương thích với mọi API theo chuẩn OpenAI (GPT-4o, Qwen, Claude, v.v.), dùng cho sinh ontology, tạo hồ sơ tác nhân, và tổng hợp báo cáo.

---

## 3. Quy Trình Hoạt Động (5 Bước)

### Bước 1 — Xây Dựng Đồ Thị Tri Thức (Graph Build)

**Mục đích:** Chuyển đổi tài liệu đầu vào thô thành cấu trúc tri thức có thể lý luận.

**Đầu vào:** File PDF, Markdown, hoặc TXT (tối đa 50MB) + mô tả yêu cầu mô phỏng bằng ngôn ngữ tự nhiên.

**Quy trình chi tiết:**

```
Tài liệu thô
     │
     ▼
[File Parser] ─── Trích xuất văn bản (hỗ trợ PDF, MD, TXT)
                  Xử lý encoding đa ngôn ngữ
     │
     ▼
[LLM - OntologyGenerator] ─── Phân tích nội dung
                               Xác định loại thực thể (EntityType)
                               Xác định loại quan hệ (EdgeType)
                               Trả về JSON ontology chuẩn
     │
     ▼
[Text Chunker] ─── Chia văn bản thành chunks (mặc định 500 từ, overlap 50)
     │
     ▼
[Zep GraphBuilder] ─── Gửi từng batch (3 chunks) lên Zep Cloud
                        Zep tự động trích xuất thực thể & quan hệ
                        Xây dựng Standalone Graph
                        Cập nhật bộ nhớ dài hạn (GraphRAG)
```

**Đầu ra:** Graph ID lưu trên Zep Cloud, bao gồm các node (thực thể) và edge (quan hệ) được trích xuất từ tài liệu.

**Kỹ thuật đặc biệt:**
- Xử lý song song bất đồng bộ (async threading) để không block UI
- Polling tiến độ theo thời gian thực qua Task Manager
- Hiển thị đồ thị tương tác bằng D3.js ngay khi đang xây dựng

---

### Bước 2 — Thiết Lập Môi Trường Mô Phỏng (Environment Setup)

**Mục đích:** Chuyển đổi các thực thể trong đồ thị thành các tác nhân OASIS có đầy đủ hồ sơ nhân vật.

**Giai đoạn 2a — Đọc & Lọc Thực Thể từ Zep:**
- Gọi Zep API để lấy toàn bộ node trong graph
- Lọc các node có loại thực thể cụ thể (không chỉ là `Entity` chung)
- Làm giàu thông tin: tải các edge liên quan đến từng node

**Giai đoạn 2b — Tạo Hồ Sơ Tác Nhân (Profile Generation):**
```
Thực thể từ Zep
     │
     ▼
[LLM - OasisProfileGenerator]
     │
     ├─── Phân tích thông tin thực thể (tên, mô tả, quan hệ)
     ├─── Sinh persona: tuổi, giới tính, MBTI, nghề nghiệp, quốc gia
     ├─── Xác định chủ đề quan tâm (interested_topics)
     ├─── Tạo tiểu sử (bio) và nhân cách (persona) chi tiết
     │
     ▼
OasisAgentProfile (chuẩn Twitter & Reddit)
```

**Giai đoạn 2c — Tạo Cấu Hình Mô Phỏng:**
- LLM phân tích yêu cầu mô phỏng của người dùng
- Tự động xác định số vòng mô phỏng (mặc định đề xuất 40)
- Cho phép người dùng tùy chỉnh số vòng qua slider
- Xuất file `simulation_config.json` và `twitter_profiles.json` / `reddit_profiles.json`

**Thông tin trong mỗi hồ sơ tác nhân:**

| Trường | Mô Tả |
|---|---|
| `user_id` | ID định danh duy nhất |
| `user_name` | Tên người dùng trong mạng xã hội |
| `name` | Tên thực |
| `bio` | Tiểu sử |
| `persona` | Nhân cách, lối suy nghĩ, cách phản ứng |
| `age`, `gender`, `mbti` | Thông tin nhân khẩu học |
| `interested_topics` | Danh sách chủ đề quan tâm |
| `karma` / `follower_count` | Chỉ số mạng xã hội (Reddit/Twitter) |

---

### Bước 3 — Chạy Mô Phỏng (Simulation)

**Mục đích:** Chạy mô phỏng hành vi xã hội của các tác nhân trên hai nền tảng song song.

**Kiến trúc chạy mô phỏng:**

```
SimulationManager
     │
     ├─── SimulationRunner (chạy trong subprocess riêng biệt)
     │         │
     │         ├─── OASIS Twitter Simulation
     │         │         └─── Các action: CREATE_POST, LIKE_POST,
     │         │                          REPOST, FOLLOW, QUOTE_POST,
     │         │                          DO_NOTHING
     │         │
     │         └─── OASIS Reddit Simulation
     │                   └─── Các action: CREATE_POST, CREATE_COMMENT,
     │                                    LIKE_POST, DISLIKE_POST,
     │                                    LIKE_COMMENT, DISLIKE_COMMENT,
     │                                    SEARCH_POSTS, SEARCH_USER,
     │                                    TREND, FOLLOW, MUTE, REFRESH,
     │                                    DO_NOTHING
     │
     └─── ZepGraphMemoryUpdater (chạy song song)
               └─── Cập nhật bộ nhớ đồ thị Zep theo thời gian thực
                    sau mỗi hành động của tác nhân
```

**Tính năng đặc biệt của mô phỏng:**

- **IPC (Inter-Process Communication):** Giao tiếp giữa process chính và OASIS subprocess qua socket, cho phép điều khiển (start/pause/stop) và theo dõi trạng thái
- **Cập nhật bộ nhớ theo thời gian thực:** Mỗi hành động của tác nhân được ghi vào Zep Graph ngay lập tức, đảm bảo bộ nhớ luôn phản ánh trạng thái hiện tại
- **Theo dõi tiến độ:** Frontend polling API để hiển thị số vòng đã chạy, số hành động đã thực hiện, log chi tiết từng tác nhân

**Vòng đời mô phỏng:**

```
IDLE → STARTING → RUNNING → [PAUSED ↔ RUNNING] → STOPPING → COMPLETED
                                                           └→ FAILED
```

---

### Bước 4 — Tạo Báo Cáo (Report Generation)

**Mục đích:** ReportAgent tự động phân tích kết quả mô phỏng và tạo báo cáo chuyên sâu.

**Kiến trúc ReportAgent (ReAct Pattern):**

```
Yêu cầu phân tích của người dùng
     │
     ▼
[ReportAgent - LLM điều phối]
     │
     ├── Lập kế hoạch (Planning): Xác định cấu trúc báo cáo
     │
     ├── Vòng lặp ReAct (tối đa 5 lần gọi công cụ):
     │    ├── 🔧 search_graph_facts — Tìm kiếm sự kiện trong đồ thị Zep
     │    ├── 🔧 insight_forge — Tổng hợp insight từ nhiều thực thể
     │    ├── 🔧 panorama_view — Xem toàn cảnh quan hệ và xu hướng
     │    └── 🔧 agent_interview — Phỏng vấn tác nhân cụ thể
     │
     ├── Phản ánh (Reflection): Đánh giá và bổ sung nội dung (tối đa 2 vòng)
     │
     └── Hoàn thiện báo cáo cuối cùng
```

**Các công cụ của ReportAgent:**

| Công Cụ | Chức Năng |
|---|---|
| `search_graph_facts` | Tìm kiếm sự kiện liên quan trong đồ thị Zep (node, edge, episode) |
| `insight_forge` | Tổng hợp insight toàn diện về một thực thể (lịch sử, quan hệ, xu hướng) |
| `panorama_view` | Nhìn toàn cảnh toàn bộ mạng lưới quan hệ trong graph |
| `agent_interview` | Phỏng vấn trực tiếp tác nhân OASIS với danh sách câu hỏi |

**Cấu trúc báo cáo được sinh ra:**
- Phân tích con câu hỏi (sub-question analysis)
- Sự kiện then chốt (key facts)
- Thực thể cốt lõi (core entities) và chuỗi quan hệ
- Sự kiện có hiệu lực & đã hết hạn
- Phỏng vấn các nhân vật đại diện (chọn lọc tự động)
- Tóm tắt và quan điểm cốt lõi

---

### Bước 5 — Tương Tác Sâu (Deep Interaction)

**Mục đích:** Cho phép người dùng trực tiếp trò chuyện với bất kỳ tác nhân nào đã tham gia mô phỏng.

**Hai loại tương tác:**

**5a. Phỏng vấn Tác Nhân OASIS:**
- Chọn bất kỳ tác nhân Twitter hoặc Reddit từ danh sách
- Gửi câu hỏi tùy ý — tác nhân trả lời dựa trên nhân vật, bộ nhớ, và hành động đã thực hiện
- Tối ưu hóa prompt tự động (prefix đặc biệt tránh tác nhân gọi công cụ thay vì trả lời trực tiếp)

**5b. Trò Chuyện với ReportAgent:**
- Chat với agent báo cáo để đặt câu hỏi chuyên sâu
- ReportAgent có quyền truy cập đầy đủ vào toàn bộ đồ thị Zep
- Sử dụng lại 4 công cụ phân tích để trả lời câu hỏi ad-hoc

**Giao diện split-panel:**
- Panel trái: Danh sách tác nhân và lịch sử chat
- Panel phải: Hiển thị đồ thị quan hệ liên quan đến cuộc trò chuyện

---

## 4. Các Thành Phần Kỹ Thuật

### Backend Services

| Service | Tệp | Chức Năng |
|---|---|---|
| `OntologyGenerator` | `services/ontology_generator.py` | Gọi LLM phân tích tài liệu, sinh định nghĩa ontology (entity types, edge types) |
| `GraphBuilderService` | `services/graph_builder.py` | Chia nhỏ văn bản, gửi batch lên Zep, quản lý tác vụ xây dựng đồ thị |
| `TextProcessor` | `services/text_processor.py` | Chunk văn bản theo kích thước cố định với overlap |
| `ZepEntityReader` | `services/zep_entity_reader.py` | Đọc và lọc node/edge từ Zep Graph (hỗ trợ phân trang) |
| `OasisProfileGenerator` | `services/oasis_profile_generator.py` | Chuyển thực thể Zep → hồ sơ OASIS Agent chuẩn Twitter/Reddit |
| `SimulationConfigGenerator` | `services/simulation_config_generator.py` | LLM tự động sinh cấu hình mô phỏng từ yêu cầu người dùng |
| `SimulationManager` | `services/simulation_manager.py` | Quản lý vòng đời các phiên mô phỏng, trạng thái, metadata |
| `SimulationRunner` | `services/simulation_runner.py` | Chạy OASIS trong subprocess, IPC, theo dõi hành động từng tác nhân |
| `ZepGraphMemoryUpdater` | `services/zep_graph_memory_updater.py` | Cập nhật bộ nhớ đồ thị Zep sau mỗi hành động mô phỏng |
| `ReportAgent` | `services/report_agent.py` | ReAct agent tổng hợp báo cáo với 4 công cụ phân tích Zep |
| `ZepToolsService` | `services/zep_tools.py` | Wrapper 4 công cụ Zep dành cho ReportAgent |

### Backend Utils

| Utility | Tệp | Chức Năng |
|---|---|---|
| `FileParser` | `utils/file_parser.py` | Trích xuất văn bản từ PDF (pdfplumber), MD, TXT với xử lý encoding đa ngôn ngữ |
| `LLMClient` | `utils/llm_client.py` | Client thống nhất gọi LLM API theo chuẩn OpenAI |
| `TaskManager` | `models/task.py` | Quản lý tác vụ bất đồng bộ với trạng thái và metadata |
| `ProjectManager` | `models/project.py` | Lưu trữ và quản lý thông tin dự án (graph ID, simulation ID, v.v.) |
| `ZepPaging` | `utils/zep_paging.py` | Phân trang khi lấy toàn bộ node/edge từ Zep |
| `RetryUtil` | `utils/retry.py` | Cơ chế thử lại với exponential backoff cho các API call |
| `Logger` | `utils/logger.py` | Cấu hình logging đồng nhất toàn hệ thống |

### Frontend Components

| Component | Tệp | Chức Năng |
|---|---|---|
| `Step1GraphBuild` | `components/Step1GraphBuild.vue` | Upload file, theo dõi tiến độ xây dựng đồ thị, log chi tiết |
| `Step2EnvSetup` | `components/Step2EnvSetup.vue` | Khởi tạo simulation, polling sinh hồ sơ tác nhân, cấu hình số vòng |
| `Step3Simulation` | `components/Step3Simulation.vue` | Giao diện chạy mô phỏng, hiển thị log hành động real-time |
| `Step4Report` | `components/Step4Report.vue` | Hiển thị báo cáo phong phú: phỏng vấn, sự kiện, phân tích đồ thị |
| `Step5Interaction` | `components/Step5Interaction.vue` | Chat với tác nhân/ReportAgent, split-panel với đồ thị |
| `GraphPanel` | `components/GraphPanel.vue` | Render đồ thị D3.js tương tác, xử lý self-loop, highlight node/edge |
| `HistoryDatabase` | `components/HistoryDatabase.vue` | Lịch sử các dự án đã chạy |

---

## 5. API Backend

### Graph API (`/api/graph`)

| Endpoint | Method | Mô Tả |
|---|---|---|
| `/upload` | POST | Upload file và tạo graph (trả về `task_id`) |
| `/status/<task_id>` | GET | Kiểm tra trạng thái xây dựng đồ thị |
| `/info/<graph_id>` | GET | Lấy thông tin graph (số node, edge, loại thực thể) |
| `/nodes/<graph_id>` | GET | Lấy danh sách node (hỗ trợ filter theo loại) |
| `/edges/<graph_id>` | GET | Lấy danh sách edge |
| `/node/<node_uuid>` | GET | Chi tiết một node (bao gồm episodes bộ nhớ) |

### Simulation API (`/api/simulation`)

| Endpoint | Method | Mô Tả |
|---|---|---|
| `/entities/<graph_id>` | GET | Đọc thực thể từ Zep Graph |
| `/prepare` | POST | Tạo simulation instance, sinh hồ sơ và cấu hình |
| `/prepare/status/<sim_id>` | GET | Trạng thái quá trình sinh hồ sơ tác nhân |
| `/prepare/profiles/<sim_id>` | GET | Lấy danh sách hồ sơ tác nhân đã sinh |
| `/run` | POST | Bắt đầu chạy mô phỏng OASIS |
| `/status/<sim_id>` | GET | Trạng thái mô phỏng (round hiện tại, log, v.v.) |
| `/pause/<sim_id>` | POST | Tạm dừng mô phỏng |
| `/resume/<sim_id>` | POST | Tiếp tục mô phỏng |
| `/stop/<sim_id>` | POST | Dừng hẳn mô phỏng |
| `/interview` | POST | Phỏng vấn tác nhân OASIS cụ thể |
| `/results/<sim_id>` | GET | Kết quả mô phỏng (danh sách hành động) |

### Report API (`/api/report`)

| Endpoint | Method | Mô Tả |
|---|---|---|
| `/generate` | POST | Bắt đầu tạo báo cáo (trả về `report_id`) |
| `/status/<report_id>` | GET | Trạng thái và nội dung báo cáo đang tạo |
| `/chat` | POST | Chat với ReportAgent |
| `/search` | POST | Tìm kiếm trực tiếp trên đồ thị Zep |

---

## 6. Cấu Hình & Triển Khai

### Biến Môi Trường (`.env`)

```env
# === LLM Configuration ===
# Tương thích mọi API theo chuẩn OpenAI
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL_NAME=qwen-plus

# === Zep Cloud ===
# Đăng ký miễn phí tại: https://app.getzep.com/
ZEP_API_KEY=your_zep_api_key

# === Flask Server ===
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
FLASK_DEBUG=True

# === OASIS Simulation ===
OASIS_DEFAULT_MAX_ROUNDS=10

# === Report Agent Tuning ===
REPORT_AGENT_MAX_TOOL_CALLS=5
REPORT_AGENT_MAX_REFLECTION_ROUNDS=2
REPORT_AGENT_TEMPERATURE=0.5
```

### Khởi Động Nhanh (Source Code)

```bash
# 1. Clone và cấu hình
git clone https://github.com/666ghj/MiroFish.git
cd MiroFish
cp .env.example .env
# Điền LLM_API_KEY và ZEP_API_KEY vào .env

# 2. Cài đặt toàn bộ dependencies
npm run setup:all

# 3. Chạy hệ thống
npm run dev
# Frontend: http://localhost:3000
# Backend:  http://localhost:5001
```

### Triển Khai Docker

```bash
cp .env.example .env
# Điền API keys
docker compose up -d
```

### Yêu Cầu Hệ Thống

| Thành Phần | Phiên Bản |
|---|---|
| Node.js | ≥ 18 |
| Python | ≥ 3.11, ≤ 3.12 |
| uv (Python package manager) | Latest |

---

## 7. Công Nghệ Sử Dụng

### Backend
- **Flask** — Web framework Python nhẹ, hỗ trợ multi-threading
- **Zep Cloud SDK** — Dịch vụ bộ nhớ đồ thị (Graph Memory + GraphRAG)
- **OASIS** — Framework mô phỏng mạng xã hội đa tác nhân (CAMEL-AI)
- **OpenAI SDK** — Client LLM tương thích đa nhà cung cấp
- **pdfplumber** — Trích xuất văn bản từ PDF
- **charset_normalizer / chardet** — Xử lý encoding đa ngôn ngữ

### Frontend
- **Vue 3** (Composition API) — Framework UI phản ứng
- **Vite** — Build tool hiệu năng cao
- **D3.js** — Trực quan hóa đồ thị tri thức tương tác
- **Axios** — HTTP client với interceptor và cơ chế retry
- **Marked / DOMPurify** — Render Markdown an toàn trong báo cáo

### DevOps
- **Docker + Docker Compose** — Container hóa toàn bộ stack
- **GitHub Actions** — CI/CD tự động build Docker image

---

*Tài liệu này được tổng hợp từ mã nguồn dự án MiroFish — Phiên bản: tháng 3/2026*
