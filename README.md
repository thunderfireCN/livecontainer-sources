# LiveContainer 源

给 LiveContainer 用的 AltStore 格式源，**每个 App 单独一个源链接**，和 INSAV、iPadn 官方源一个格式。加到 LiveContainer 的「源」里就能直接点安装 / 更新，不用再去 GitHub 翻。

## 源链接（点深链直接加，粘贴链接也行）

| App | 已装版本 | 源里最新 | 源链接 |
| --- | --- | --- | --- |
| AirBeep | 2.5.2 | 2.5.2 | https://raw.githubusercontent.com/thunderfireCN/livecontainer-sources/main/airbeep.json |
| AvPlay | 2.2.0 | 2.2.2 | https://raw.githubusercontent.com/thunderfireCN/livecontainer-sources/main/avplay.json |
| Cloudn | 1.4.1 | 1.4.1 | https://raw.githubusercontent.com/thunderfireCN/livecontainer-sources/main/cloudn.json |
| HGhubX | 未装 | 2.1.2 | https://raw.githubusercontent.com/thunderfireCN/livecontainer-sources/main/hghubx.json |

点下面链接直接在 LiveContainer 里添加：

- [添加 AirBeep 源](livecontainer://source?url=https%3A%2F%2Fraw.githubusercontent.com%2FthunderfireCN%2Flivecontainer-sources%2Fmain%2Fairbeep.json)
- [添加 AvPlay 源](livecontainer://source?url=https%3A%2F%2Fraw.githubusercontent.com%2FthunderfireCN%2Flivecontainer-sources%2Fmain%2Favplay.json)
- [添加 Cloudn 源](livecontainer://source?url=https%3A%2F%2Fraw.githubusercontent.com%2FthunderfireCN%2Flivecontainer-sources%2Fmain%2Fcloudn.json)
- [添加 HGhubX 源](livecontainer://source?url=https%3A%2F%2Fraw.githubusercontent.com%2FthunderfireCN%2Flivecontainer-sources%2Fmain%2Fhghubx.json)

手动加：LiveContainer → 源 → 点 `+` → 粘贴上面对应链接 → 确认。

## 注意

- **AvPlay 2.2.2 包名变了**：从 `com.javdb.avplay` 改成 `com.javdb.avplay2`，和已装的 2.2.0 不是同一个包名，点安装会是第二个 AvPlay，数据不互通，作者在更新说明里也提醒 iOS 用户先用云备份。旧的 2.2.0 确认新版没问题后可以删掉。
- **HGhubX 已加入**：原仓库 Minireel/HGhub 已删库停更，zxsos/HGhubX 是后续分支，最新 2.1.2；包名 `com.hghubx.app` 与旧版 HGhub 不同，装上是另一个 App，旧版 1.2.19 的收藏与观看记录不会带过来，确认新版没问题后可以删掉旧的。官方提醒过有加卡密 / VIP 的恶意修改版，本源只用 zxsos 官方 Release 的包，别从第三方下载站下。
- AirBeep 最低 iOS 18.0，Cloudn 最低 iOS 17.0，AvPlay 最低 iOS 15.3。

## 自动更新

每天北京时间 11:00 由 GitHub Actions 自动跑 `scripts/update_sources.py`：查四家上游仓库的最新 release，下载 IPA 核对真实包名 / 版本 / 构建号，有新版就更新对应的源文件并提交。出新版后在 LiveContainer 里刷新一下源就能看到，不用再去 GitHub 翻。
