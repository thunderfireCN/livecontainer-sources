# LiveContainer 源

给 LiveContainer 用的 AltStore 格式源，**每个 App 单独一个源链接**，和 INSAV、iPadn 官方源一个格式。加到 LiveContainer 的「源」里就能直接点安装 / 更新，不用再去 GitHub 翻。

## 源链接（点深链直接加，粘贴链接也行）

| App | 已装版本 | 源里最新 | 源链接 |
| --- | --- | --- | --- |
| AirBeep | 2.5.2 | 2.5.2 | https://raw.githubusercontent.com/thunderfireCN/livecontainer-sources/main/airbeep.json |
| AvPlay | 2.2.0 | 2.2.2 | https://raw.githubusercontent.com/thunderfireCN/livecontainer-sources/main/avplay.json |
| Cloudn | 1.4.1 | 1.4.1 | https://raw.githubusercontent.com/thunderfireCN/livecontainer-sources/main/cloudn.json |

点下面链接直接在 LiveContainer 里添加：

- [添加 AirBeep 源](livecontainer://source?url=https%3A%2F%2Fraw.githubusercontent.com%2FthunderfireCN%2Flivecontainer-sources%2Fmain%2Fairbeep.json)
- [添加 AvPlay 源](livecontainer://source?url=https%3A%2F%2Fraw.githubusercontent.com%2FthunderfireCN%2Flivecontainer-sources%2Fmain%2Favplay.json)
- [添加 Cloudn 源](livecontainer://source?url=https%3A%2F%2Fraw.githubusercontent.com%2FthunderfireCN%2Flivecontainer-sources%2Fmain%2Fcloudn.json)

手动加：LiveContainer → 源 → 点 `+` → 粘贴上面对应链接 → 确认。

## 注意

- **AvPlay 2.2.2 包名变了**：从 `com.javdb.avplay` 改成 `com.javdb.avplay2`，和已装的 2.2.0 不是同一个包名，点安装会是第二个 AvPlay，数据不互通，作者在更新说明里也提醒 iOS 用户先用云备份。旧的 2.2.0 确认新版没问题后可以删掉。
- **HGhub 没放进来**：官方已经停更删库（约 2026-11-10），1.2.19 就是最后一版，没有可用的更新来源；几个 fork 要么版本更旧，要么包名不同。手上那个 1.2.19 继续用着，别从第三方下载站下所谓的新版（官方提醒过有加卡密 / VIP 的恶意修改版）。
- AirBeep 最低 iOS 18.0，Cloudn 最低 iOS 17.0，AvPlay 最低 iOS 15.3。

## 自动更新

每天北京时间 11:00 由 GitHub Actions 自动跑 `scripts/update_sources.py`：查三家上游仓库的最新 release，下载 IPA 核对真实包名 / 版本 / 构建号，有新版就更新对应的源文件并提交。出新版后在 LiveContainer 里刷新一下源就能看到，不用再去 GitHub 翻。
