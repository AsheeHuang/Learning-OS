# Learning OS 方向 Review 與 MVP 實作建議

## 整體評價

整體方向是對的，而且核心產品判斷很有價值：

> Learning OS 不應該再造一個 AI runtime，而應該定義一套能被 Claude Code / Codex 執行的學習協議。

目前 repo 只有 `README.md` 和 agent 配置，還沒有實作，因此以下是對 spec 和架構方向的 review。

## 一、目前方向最正確的部分

### 1. 把 Markdown 當作 source of truth

這是最重要的決定：

- 不依賴資料庫
- 可以放進 Git
- 人可以直接修改
- Obsidian 可以直接使用
- 換 agent 不會遺失學習狀態
- session 結束後可以繼續

這比建立一個 Learning OS backend 更符合產品目標。

### 2. `PROGRESS.md` 和 `HISTORY.md` 分離

這個 distinction 很好：

```text
PROGRESS = 現在是什麼狀態
HISTORY  = 發生過什麼事
```

很多學習系統會把「曾經讀過」誤當成「已經學會」。把 assessment 放在狀態轉換的核心，方向正確。

### 3. `lesson` 和 `note` 的區分

```text
lesson = 主線內容
note   = 探索分支
```

這能避免所有內容最後都變成一堆沒有層次的筆記。

### 4. `/explore` 是真正有差異化的功能

四個 command 裡，`/explore` 最有產品特色。

一般 AI tutor 的問題是：

1. 主 agent 被支線問題打斷
2. 回答只留在對話中
3. 下次遇到同一概念又重新解釋

把探索內容獨立成 note，並連回來源 lesson，確實能形成持久的學習網路。

### 5. MVP 範圍基本合理

先做：

```text
/learn
/explain
/explore
/quiz
```

暫時不做：

- backend
- vector database
- graph database
- Web UI
- 複雜 spaced repetition
- orchestration framework

這個取捨是對的。

## 二、現在最需要先釐清的問題

目前 spec 最大的風險不是功能太少，而是幾個關鍵 protocol 還不夠精確。若直接開始寫 skill，四個 agent 很容易產生不同格式。

### P0：Learning OS repo 和 learning workspace 的邊界

現在 spec 有：

```text
<topic>/
├── MISSION.md
├── MAP.md
...
```

但還沒定義這個 `<topic>/` 到底在哪裡。

我建議明確定義：

```text
Learning OS repository
└── skills/
    ├── learn/
    ├── explain/
    ├── explore/
    └── quiz/

Obsidian vault
└── Learn/                         ← Learning OS mother folder
    └── Operating Systems/
        ├── MISSION.md
        ├── MAP.md
        ├── PROGRESS.md
        ├── HISTORY.md
        ├── RESOURCES.md
        ├── lessons/
        ├── notes/
        ├── assessments/
        ├── flashcards/
        ├── references/
        └── assets/
```

也就是：

- Learning OS repo：放 skills 和 protocol
- Obsidian vault：放實際學習資料
- `Learn/`：Learning OS 的 mother folder，集中所有 topic workspaces
- 不應該預設把學習資料寫進 Learning OS source repo

第一版可以採用很簡單的規則：

> Agent 執行時的目前工作目錄就是 Obsidian vault；Learning OS 使用 vault 下的 `Learn/` 作為 mother folder。`/learn OS` 會建立或進入 `Learn/OS/`；`/learn Operating Systems` 則會建立或進入 `Learn/Operating Systems/`。

如果 `Learn/` 尚不存在，`/learn` 負責建立它。這個規則要寫死，否則每個 skill 都會對 workspace discovery 做不同假設。

### P0：概念名稱、檔名和 Wiki link 的 mapping

目前有一個潛在衝突：

```text
lessons/processes.md
notes/processes.md
```

兩個檔案都可能對應：

```markdown
[[Processes]]
```

如果 workspace 內有同名檔案，Obsidian 可能無法判斷要連到哪一個檔案。不過這不代表一定要禁止同名檔案；把 link 寫清楚即可解決：

```markdown
[[lessons/processes.md|Processes]]
[[notes/processes.md|Processes]]
```

第一版建議採用這個規則：

1. `lessons/` 和 `notes/` 可以有相同 basename，因為它們代表不同的內容角色。
2. 所有 agent 產生的 link 都使用相對路徑，並用 alias 保持顯示名稱乾淨。
3. 主線 lesson 使用 `[[lessons/<slug>.md|<Topic>]]`。
4. 探索 note 使用 `[[notes/<slug>.md|<Topic>]]`。
5. `PROGRESS.md` 的 `Path` 欄位記錄實際檔案路徑，避免狀態指向不明。
6. 如果 lesson 和 note 實際上是同一份內容，不要因為路徑不同而重複建立；應該更新既有檔案或明確決定要把它從 note 提升為 lesson。

例如，從 Processes lesson 連到 Context Switch exploration note：

```markdown
[[lessons/processes.md|Processes]] → [[notes/context-switch.md|Context Switch]]
```

這比要求整個 workspace 只能有一個 canonical Markdown file 更符合 `lesson = 主線`、`note = 探索分支` 的設計。MVP 也不需要額外的 naming system。

### P0：`PROGRESS.md` 需要一個唯一的 source of truth

目前 spec 同時有：

```text
## Current Focus
## Needs Validation
## Needs Review
## Progress
```

這會造成同一個狀態要被寫兩次：

- 一次寫在 section
- 一次寫在 table

最後一定會出現不同步。

建議 MVP 只讓 table 成為狀態真相：

```markdown
# Learning Progress

## Current Focus

[[lessons/virtual-memory.md|Virtual Memory]]

## Topics

| Topic | Path | Status | Last Learned | Last Tested |
|---|---|---|---|---|
| [[lessons/processes.md|Processes]] | lessons/processes.md | Mastered | 2026-08-25 | 2026-08-26 |
| [[lessons/threads.md|Threads]] | lessons/threads.md | Needs Validation | 2026-08-27 | — |
| [[notes/race-conditions.md|Race Conditions]] | notes/race-conditions.md | Needs Review | 2026-08-20 | 2026-08-21 |
```

`/quiz` 只需要解析 `Topics` table：

```text
Status == Needs Validation
```

`Needs Validation` 和 `Needs Review` section 如果想保留，可以作為 agent 產生的視圖，但不應該是第二份可編輯的資料。

### P0：狀態轉換要明確

建議先把狀態機定義成：

```text
Unexplored
    ↓ /explain
Learning
    ↓ lesson studied
Needs Validation
    ↓ /quiz
Mastered
    ↓ weak assessment
Needs Review
    ↓ /explain
Needs Validation
```

更具體一點：

| 行為 | 狀態 |
|---|---|
| `/learn` 建立 map topic | `Unexplored` |
| `/explain` 開始但尚未完成 | `Learning` |
| `/explain` 完成 lesson | `Needs Validation` |
| `/explore` 建立新 note | `Learning` 或 `Needs Validation` |
| quiz 表現良好 | `Mastered` |
| quiz 部分理解或有明顯缺口 | `Needs Review` |
| 重新學習已 Mastered topic | `Needs Validation` |

最重要的 invariant 是：

> 建立 lesson、讀完 lesson、產生 note，都不能直接產生 `Mastered`。

`Mastered` 只能由 assessment 產生。

### P0：`/explore` 的 subagent 行為要有 fallback

spec 已經寫了：

> When possible, delegate research/explanation to a subagent.

這個方向正確，但必須定義沒有 subagent 時的行為。

建議：

```text
Host supports subagents
    → delegate exploration
    → main agent later integrates the result

Host does not support subagents
    → current agent performs the exploration itself
    → same note format and same links
```

也就是：

> subagent 是 execution optimization，不是 protocol dependency。

第一版也不要要求真正的背景執行。只要做到：

- 有 subagent 時可以 delegate
- 沒有時能 fallback
- 最終輸出格式完全一致

就足夠了。

## 三、對各個檔案的建議

### `MISSION.md`

設計很好，建議保持很短，並固定格式：

```markdown
# Mission: Operating Systems

## Why

## Current Level

## Target Level

## Desired Outcomes

## Constraints

## Out of Scope
```

不要讓 agent 每次都重寫整份 mission。後續 `/learn` 應該先讀取並詢問是否要更新。

### `MAP.md`

建議區分：

```markdown
# Operating Systems

## Execution

- [[lessons/processes.md|Processes]]
- [[lessons/threads.md|Threads]]
- [[lessons/scheduling.md|Scheduling]]

## Concurrency

- [[lessons/locks.md|Locks]]
- [[lessons/semaphores.md|Semaphores]]
- [[lessons/deadlocks.md|Deadlocks]]

## Memory

- [[lessons/virtual-memory.md|Virtual Memory]]
- [[lessons/paging.md|Paging]]
- [[lessons/page-tables.md|Page Tables]]
```

MVP 階段不要要求 agent 自動建立完整 dependency graph，也不要掃描整個 workspace 自動重排 map。

`/explore` 只在以下情況更新 map：

- 該概念是主題的必要前置知識
- 該概念值得成為學習者可選擇的主線 topic
- agent 明確向使用者提出 map update，使用者同意

否則只建立 note 並從來源 lesson link 過去。

### `lessons/` 和 `notes/`

可以保留現在的區分，但每個檔案應該有一致的 metadata：

```markdown
---
type: lesson
topic: Processes
status: needs-validation
---

# Processes

## Why this matters

## Explanation

## Example

## Related concepts

- [[lessons/threads.md|Threads]]
- [[notes/context-switch.md|Context Switch]]

## Sources
```

不過不建議第一版過度依賴 YAML frontmatter。若不同 host 對 YAML 支援不一致，可以先用 Markdown heading。

比較重要的是固定：

- title
- type
- source lesson / parent concept
- related concepts
- sources

### `HISTORY.md`

這部分可以繼續保持 append-only：

```markdown
## 2026-08-28

### Learned: Processes

Created [[lessons/processes.md|Processes]].

Status:
Unexplored → Needs Validation

### Explored: Context Switch

Encountered while reading [[lessons/processes.md|Processes]].

Created [[notes/context-switch.md|Context Switch]].

Linked:
[[lessons/processes.md|Processes]] → [[notes/context-switch.md|Context Switch]]
```

建議所有事件都使用 ISO date：

```text
YYYY-MM-DD
```

不要讓 HISTORY 變成完整對話 transcript。它只需要記錄：

- 發生了什麼
- 哪個 topic
- 哪個狀態變了
- 產生了哪個檔案
- assessment 的摘要結果

### `RESOURCES.md`

這裡可以直接參考 Matt Pocock Teach skill 的 `RESOURCES-FORMAT.md`（不是 `RESOURCE.md`）。它的重點不是建立一個 URL list，而是建立這個 topic 的 curated trusted sources。

建議保留它的核心原則：

- explainers 優先從 `RESOURCES.md` 中的來源取得知識，而不是直接依賴 model memory
- 用 `Knowledge` 區分「產生 lesson 時應該使用的主要來源」
- 用 `Further Reading` 放有價值但不是每次 explain 都需要讀的延伸材料
- 每個來源除了 link，還要有一句說明，以及 `Use for` 指出它適合哪些問題
- lesson 和 note 中的重要 claims 應該附上 inline citations，讓內容可以追溯

第一版可以採用這個格式：

```markdown
# Operating Systems Resources

## Knowledge

- [Book: Operating Systems: Three Easy Pieces](https://pages.cs.wisc.edu/~remzi/OSTEP/)
  Foundational introduction to operating systems. Use for: processes, virtual memory, concurrency, and file systems.
- [Documentation: Linux Kernel Documentation](https://docs.kernel.org/)
  Primary technical documentation for Linux internals. Use for: kernel-specific behavior and implementation details.

## Further Reading

- [Book: The Linux Programming Interface](https://man7.org/tlpi/)
  Detailed reference for Linux and UNIX programming. Use for: system calls and low-level programming.
```

`/learn` 應該永遠建立 `RESOURCES.md`，至少包含 `Knowledge` 和 `Further Reading` headings。若 `Knowledge` 還是空的，`/explain` 不應該假裝 model memory 是已驗證來源，而應該要求補充來源、使用 host 提供的 research 工具，或在 lesson 中清楚標示未驗證內容。

### `assessments/`

這裡可以參考 Matt Pocock Teach skill 的教學和評估方式，但要分清楚哪些是參考、哪些是 Learning OS 自己新增的 protocol。

Teach skill 的重點是：

- lesson 應該短小，完成一個明確的 learning win
- 先教必要知識，再透過 interactive practice 讓學習者實際回答或操作
- 使用 retrieval practice，而不是只讓學習者重新閱讀內容
- 在互動過程中即時給 feedback
- 可以使用 quiz、實作題或 guided real-world steps，但 quiz 只是 lesson 裡的互動工具
- lesson 結束時提醒學習者提出 follow-up questions
- 把重要的學習洞察記錄到 learning records，供之後判斷下一個適合的學習內容

Teach skill **沒有定義正式的分數、pass/fail、mastery status 或獨立的 assessment artifact**。因此 `/quiz` 的正式評估流程是 Learning OS 根據自己的產品需求做的延伸，不是直接複製 Teach skill。

第一版 `/quiz` 建議採用 Teach 的 interactive feedback loop，而不是一次產生一大份考卷：

1. 從 `PROGRESS.md` 找出所有 `Needs Validation` topics。
2. 決定這次 assessment 要涵蓋哪些 topics。
3. 一次提出一個理解型問題。
4. 等使用者回答，不提前顯示答案。
5. 立即給 feedback，指出回答中正確的部分和缺口。
6. 必要時要求使用者修正、舉例、比較或應用，而不是只判斷對錯。
7. 將問題、原始回答、feedback、misconceptions 和結果寫入 assessment artifact。
8. 全部問題完成後，才根據整體 evidence 更新 `PROGRESS.md`。

題目應該優先測試：

- 能否用自己的話解釋概念
- 能否比較相近概念
- 能否預測一個情境的結果
- 能否把概念應用到新的例子
- 能否找出或修正自己的 misconception

不要只測試 lesson 中的句子是否被記住。如果使用選擇題，選項的長度和格式也應盡量一致，避免答案線索影響結果；但 MVP 應以 open-ended questions 和 explanation 為主。

Learning OS 可以先使用簡單的三段結果：

```text
strong  → Mastered
partial → Needs Review
weak    → Needs Review
```

這個結果分類和 `PROGRESS.md` 的狀態轉換是 Learning OS 的設計，不是 Teach skill 已經提供的 formal grading system。

建議 assessment artifact 格式：

```markdown
# Assessment: Processes and Threads

- Date: 2026-08-29
- Topics:
  - [[lessons/processes.md|Processes]]
  - [[lessons/threads.md|Threads]]

## Questions

### 1. What is a process?

Prompt:

Learner answer:

Feedback:

Evidence:

Result: strong

### 2. How is a process different from a thread?

Prompt:

Learner answer:

Feedback:

Evidence:

Result: partial

## Misconceptions

## Summary

## Progress changes
```

Assessment 應在使用者回答之後才補上 `Learner answer`、`Feedback`、`Evidence` 和 `Result`，避免 agent 先把答案或評估結果寫出來。

## 四、我會怎麼做

我不會現在立刻寫四個 skill。會先建立一個很小但精確的 protocol，再用它約束四個 skill。

### Phase 0：先定義 MVP protocol

只需要一個文件：

```text
docs/learning-protocol.md
```

內容定義：

- workspace discovery
- 檔案結構
- topic naming
- wiki-link 規則
- progress status enum
- status transitions
- history event format
- assessment format
- subagent fallback
- source/citation 規則

再建立一個 fixture：

```text
examples/operating-systems/
├── MISSION.md
├── MAP.md
├── PROGRESS.md
├── HISTORY.md
├── RESOURCES.md
├── lessons/
├── notes/
└── assessments/
```

這個 example 同時也是：

- 文件
- 手動測試 fixture
- agent 產出範例
- 未來 regression test 的基礎

### Phase 1：實作 `/learn`

目標只有：

```text
/learn Operating Systems
```

能夠：

1. 建立或找到 topic workspace
2. 問 mission 問題
3. 建立 `MISSION.md`
4. 建立 `RESOURCES.md`；有 research 能力時先整理可信來源
5. 根據 mission 和 resources 建立 bounded、breadth-first 的 `MAP.md`
6. 建立初始 `PROGRESS.md`
7. 建立 `HISTORY.md`
8. 驗證 workspace 一致性並顯示 map
9. 問使用者選哪個 topic

Acceptance criteria：

- 不會生成所有 lesson
- map 是 breadth-first
- topic 初始狀態是 `Unexplored`
- 可以中斷後重新執行並 resume

### Phase 2：實作 `/explain`

目標：

```text
/explain Processes
```

能夠：

1. 讀 `MISSION.md`
2. 讀 `MAP.md`
3. 讀 `PROGRESS.md`
4. 讀相關 resources
5. 建立或更新 `lessons/processes.md`
6. 加入相關 wiki links
7. 將狀態更新成 `Needs Validation`
8. append 一筆 HISTORY event

這一階段先不要自動探索，不要 delegate subagent。先確保主流程可靠。

### Phase 3：實作 `/quiz`

這是 validation gate，也是 MVP 最重要的功能。

目標：

```text
/quiz
```

能夠：

1. 從 `PROGRESS.md` 找出所有 `Needs Validation`
2. 允許一次測試多個 topics
3. 讀取相關 lesson/note
4. 產生理解型問題
5. 等使用者回答
6. 寫 assessment artifact
7. 更新 topic status
8. append HISTORY 摘要

先只使用三種結果：

```text
strong  → Mastered
partial → Needs Review
weak    → Needs Review
```

不要在 MVP 做複雜分數、ELO、間隔重複演算法或統計模型。

### Phase 4：實作 `/explore`

最後再加入 subagent integration。

目標：

```text
/explore context switch
```

能夠：

1. 從目前 lesson 或使用者輸入判斷來源
2. 建立 `notes/context-switch.md`
3. link 回來源 lesson
4. link 到相關已存在概念
5. 可選擇更新 `MAP.md`
6. 將 topic 加入 `PROGRESS.md`
7. append HISTORY
8. 有 subagent 時 delegate，否則 fallback 到目前 agent

這樣可以先證明核心 learning loop，再加入最有特色但也最依賴 host 能力的功能。

## 五、我會先建立的 repo 結構

在 Learning OS repository 中，第一版只有：

```text
learning-os/
├── README.md
├── AGENTS.md
├── docs/
│   ├── agents/
│   └── learning-protocol.md
├── skills/
│   ├── learn/
│   │   └── SKILL.md
│   ├── explain/
│   │   └── SKILL.md
│   ├── explore/
│   │   └── SKILL.md
│   └── quiz/
│       └── SKILL.md
└── examples/
    └── operating-systems/
        ├── MISSION.md
        ├── MAP.md
        ├── PROGRESS.md
        ├── HISTORY.md
        ├── RESOURCES.md
        ├── lessons/
        ├── notes/
        └── assessments/
```

第一版不需要：

```text
src/
packages/
server/
database/
api/
graph/
```

Skill 內容應該是 agent instruction，不是 TypeScript 程式。

另外，Codex 和 Claude Code 的 skill discovery 方式可能不同，因此應該把：

- protocol
- workspace format
- behaviour contract

放在共用文件裡，再提供很薄的 host-specific install/adaptor。不要讓兩個 host 各自發展一套不同邏輯。

## 六、目前 spec 應該縮減的部分

README 現在還列出：

```text
/flashcards
/review
/organize
```

我會把它們明確標成 post-MVP，而不是讓使用者以為已經是第一版承諾。

第一版成功條件應該只有：

> 在一個乾淨的 Obsidian vault 中，Learning OS 能建立 `Learn/<topic>/` workspace；使用者可以執行 `/learn`、選擇 topic、執行 `/explain`，探索一個 side concept，最後執行 `/quiz`，而所有狀態都能從 Markdown 恢復。

如果這個 loop 不順，增加 flashcards 或 organize 不會改善產品。

## 七、以 Wayfinder 的角度，接下來應該先決定什麼

這個 effort 已經大到不適合直接開工。我會把 destination 定義成：

> 一套可安裝到 Claude Code 或 Codex 的四技能 Markdown protocol，能在乾淨的 Obsidian vault 內透過 `Learn/<topic>/` 完成 Map → Learn → Explore → Validate，且所有學習狀態都持久化在可編輯的 Markdown 中，不需要 backend 或 custom runtime。

第一批 decision tickets 應該是：

1. **Define the Learning Workspace Boundary**  
   決定 vault、topic directory 和 Learning OS source repo 的關係。

2. **Define Canonical Topic Identity and Wiki Links**  
   決定 topic title、filename、lesson/note 和 Obsidian link 的 mapping。

3. **Define the Progress State Machine**  
   決定 status、table format 和每個 command 的狀態轉換。

4. **Define Cross-Agent and Subagent Behavior**  
   決定 Claude Code、Codex 和無 subagent host 的共同 fallback contract。

5. **Define the Minimal Skill Output Contract**  
   決定四個 skill 必須建立、更新和保留哪些檔案。

這些決定完成後，實作應該會相當直接。

## 結論

我會保留目前的核心方向，但在寫 skill 前先補上四件事：

1. workspace 邊界
2. topic/link identity
3. progress state machine
4. host/subagent fallback

其中最需要立刻修改的是 `PROGRESS.md` 的雙重狀態表示，以及 `lessons/` / `notes/` 可能造成的 Wiki link collision。

我不會先做 backend，也不會先做 graph automation。第一個可用版本應該只是一組清楚的 Markdown skill instructions，加上一個可手動測試的 example workspace。
