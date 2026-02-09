---
name: claude-md-generator
description: 为项目生成高质量的 CLAUDE.md 配置文件。当用户请求创建项目配置、初始化 Claude Code 设置或编写编码规范时使用。遵循 100 行原则，包含技术栈、项目结构、常用命令、代码规范和工作流限制五大核心模块。
---
# CLAUDE.md 生成器

## 核心原则

### 1. 简洁性：100 行原则

- CLAUDE.md 必须控制在 100 行以内
- 只包含 AI 编码时真正需要的信息
- 避免冗长的介绍和重复说明

### 2. 特定性：说人话，别模糊

- 每条规则必须是可执行、可验证的
- 避免使用"保持简洁"、"遵循最佳实践"等模糊表述
- 使用具体数值和明确要求

### 3. 可迭代性：随时更新

- 项目技术栈变更时立即更新配置
- 发现 AI 行为不符合预期时添加规则
- 使用 `#` 键快速引用和编辑

## 必须包含的 5 个内容模块

### 模块 1：技术栈声明

- 明确列出框架、库和版本号
- 区分前端、后端、共享依赖
- 示例格式：

```markdown
# 技术栈
**前端**
- Next.js 14 (App Router)
- React 18 (Server Components优先)
- TypeScript 5.2
- Tailwind CSS 3.4

**后端**
- Node.js 20 LTS
- Express 4.18
- Prisma ORM
- PostgreSQL 15
```

### 模块 2：项目结构说明

- 说明关键目录的用途
- 定义文件命名规范
- 特别说明 `docs` 目录用于存放指导文档和资料
- 示例格式：

```markdown
# 项目结构
src/
├── app/              # 页面路由
├── components/       # 可复用UI组件
├── lib/              # 工具函数和hooks
├── services/         # API调用层
└── docs/             # 指导文档和资料
# 文件命名
- 组件：PascalCase (UserProfile.tsx)
- 工具函数：camelCase (formatDate.ts)
- 常量：UPPER_SNAKE_CASE (API_BASE_URL)
```

### 模块 3：常用命令

- 列出开发、测试、构建命令
- 包含数据库相关命令
- 示例格式：

```markdown
# 开发命令
npm run dev          # 启动开发服务器
npm run build        # 生产构建
npm run test         # 运行测试
npm run lint         # 代码检查
```

### 模块 4：代码风格规范

- 使用 MUST/SHOULD/COULD 区分优先级
- 使用对比法（✅/❌）展示正确与错误做法
- 示例格式：

```markdown
# 代码规范
**MUST (必须遵守)**
- MUST 使用 TypeScript 严格模式
- MUST 为所有 API 添加错误处理

**SHOULD (推荐遵守)**
- SHOULD 组件不超过 200 行
- SHOULD 提取重复逻辑为自定义 Hook

# 状态更新规范
❌ 错误：直接修改 state
const [user, setUser] = useState({name: 'John', age: 30});
user.age = 31; // 错误！

✅ 正确：使用不可变更新
setUser(prev => ({...prev, age: 31}));
```

# 限制事项

- ❌ 不要修改 `/prisma/schema.prisma` (需团队评审)
- ❌ 不要安装新依赖包 (需在 package.json review 时讨论)
- ❌ 不要修改 `/lib/auth/*` (认证逻辑敏感)
- ✅ 可以自由修改 `/components` 和 `/app` 下的业务代码

## 实战技巧

### 技巧 1：用 SHOULD/MUST 强调优先级

- MUST：必须遵守的规则
- SHOULD：推荐遵守的规则
- COULD：可选的规则

### 技巧 2：示例代码胜过千言万语

- 与其描述规范，不如直接给示例
- 提供完整的代码片段供参考

### 技巧 3：分层配置管理（Monorepo 必备）

- 根目录定义通用规范
- 子模块定义特定配置
- 子配置继承并覆盖根配置

### 技巧 4：用 ❌ 和 ✅ 做对比

- 展示错误做法和正确做法
- 让规则一目了然

### 技巧 5：记录常见错误模式

- 把团队经常犯的错误写进去
- 让 AI 帮你把关

### 技巧 6：链接到详细文档

- CLAUDE.md 保持简洁
- 链接到详细文档获取更多信息

## 常见错误和避坑指南

### 坑 1：文件太长，塞一切内容

- 问题：占用太多 token，稀释重要信息
- 解决：严格控制在 100 行以内

### 坑 2：从不更新配置

- 问题：过时的配置导致 AI 生成错误代码
- 解决：养成习惯，每次重大重构后更新

### 坑 4：过于笼统的规则

- 问题：AI 无法执行，等于没写
- 解决：每条规则必须具体、可验证、可执行

### 坑 5：敏感信息泄露

- 问题：配置文件会提交到仓库，敏感信息泄露
- 解决：只描述配置方式，不写具体值

## 生成 CLAUDE.md 的步骤

1. **分析项目**：读取 package.json、tsconfig.json 等配置文件
2. **识别技术栈**：提取框架、库和版本信息
3. **确定项目结构**：分析目录结构，识别关键目录
4. **提取常用命令**：从 package.json 的 scripts 中提取
5. **推断代码规范**：根据 ESLint、Prettier 等配置推断
6. **生成配置文件**：按照五大模块结构生成 CLAUDE.md
7. **验证行数**：确保文件不超过 100 行

## 示例输出

```markdown
# 项目名称

## 技术栈
- React 18.2 (Hooks优先，避免Class组件)
- TypeScript 5.2 (严格模式)
- TailwindCSS 3.4 (utilities优先)

## 项目结构
src/
├── app/              # 页面路由
├── components/       # 可复用UI组件
├── lib/              # 工具函数和hooks
├── services/         # API调用层
└── docs/             # 指导文档和资料

## 常用命令
npm run dev      # 启动开发服务器
npm run build    # 生产构建
npm run test     # 运行测试
npm run lint     # 代码检查

## 代码规范
**MUST (必须遵守)**
- MUST 使用 TypeScript 严格模式
- MUST 为所有 API 添加错误处理

**SHOULD (推荐遵守)**
- SHOULD 组件不超过 200 行
- SHOULD 提取重复逻辑为自定义 Hook

## 工作流和限制
- ❌ 不要修改 `/lib/auth/*` (认证逻辑敏感)
- ❌ 不要安装新依赖包 (需团队讨论)
- ✅ 可以自由修改 `/components` 和 `/app` 下的业务代码
```

## 注意事项

- 生成的 CLAUDE.md 必须是中文
- 代码注释使用中文
- 遵循用户的自定义编码规范（变量命名、函数命名等）
- 确保文件路径使用正斜杠（Unix 风格）
- 避免在配置中包含敏感信息
