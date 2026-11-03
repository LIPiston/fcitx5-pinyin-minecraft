# Minecraft dictionary for fcitx5-pinyin / 用于 fcitx5 拼音输入法的 Minecraft 词典

## About this project / 关于本项目

This repository is a rebuild of [oldherl/fcitx5-pinyin-minecraft](https://github.com/oldherl/fcitx5-pinyin-minecraft),
which generated an fcitx5 pinyin dictionary from the page titles of
[中文 Minecraft Wiki](https://zh.minecraft.wiki/). That repository is gone, so this one
carries the code forward and rebuilds the dictionary automatically every week.

本仓库重建自 [oldherl/fcitx5-pinyin-minecraft](https://github.com/oldherl/fcitx5-pinyin-minecraft)。
原仓库已删除，这里沿用其代码，并改为每周自动重新构建词库。

## Upstream projects / 上游项目

### mw2fcitx

- Original name `fcitx5-pinyin-moegirl`. The old
  [v1 branch](https://github.com/outloudvi/mw2fcitx/tree/v1) is what `oldherl` started from.

### Minecraft Wiki

- All entries come from page titles of [中文 Minecraft Wiki](https://zh.minecraft.wiki/).
- Thanks to all contributors for releasing the content under a free license and
  providing the API to download it.

## Installation / 安装

### From the nightly release

Every Saturday the dictionary is rebuilt and published to the fixed
[`nightly` release](https://github.com/LIPiston/fcitx5-pinyin-minecraft/releases/tag/nightly).
The tag is reused, so the download URL never changes:

```
https://github.com/LIPiston/fcitx5-pinyin-minecraft/releases/download/nightly/minecraft-cn.dict
```

1. Download `minecraft-cn.dict`.
2. Copy it to `/usr/share/fcitx5/pinyin/dictionaries/` (for fcitx5-pinyin),
   or import it from the fcitx5 configuration tool.

### AUR / [archlinuxcn] repo

- TODO.

## Build / 构建

Requirements:

- `libime` — provides the `libime_pinyindict` command
  (<https://github.com/fcitx/libime/>)
- Python modules: `opencc` (<https://pypi.org/project/OpenCC/>) and
  `pypinyin` (<https://pypi.org/project/pypinyin/>)

```sh
make build          # produces minecraft-cn.dict
make clean          # removes generated files
```

The build downloads every page title from the wiki, collates the titles into
dictionary entries, converts them to simplified Chinese with pinyin, and
compiles the result with `libime_pinyindict`. See the `Makefile` for the
individual steps.

### Tests

```sh
python -m pytest tests/ -q
```

`tests/test.sh` builds the dictionary from a checked-in title list, skipping the
network fetch.

## Automation / 自动构建

`.github/workflows/weekly.yml` runs every Saturday at 04:17 Beijing time
(Friday 20:17 UTC):

1. installs `libime` and the Python dependencies,
2. runs the test suite,
3. rebuilds `minecraft-cn.dict` from the live wiki,
4. uploads the dictionary as a workflow artifact,
5. moves the `nightly` tag to the built commit and replaces the release asset.

The job can also be started by hand from the Actions tab (`workflow_dispatch`).

Fetching uses one bulk query per page of results (`generator=allpages` with
`inprop=varianttitles`) instead of one request per title, so a full rebuild makes
about 60 requests rather than tens of thousands. From a home connection that is
about 90 seconds; GitHub's runners are throttled by the wiki to roughly one
request per 50 seconds, so a run takes about 45 minutes — hence the 150-minute
job timeout. The job fails instead of publishing if fewer than 5000 entries come
out, so a half-finished fetch never replaces the release asset.

## License

### Code in this project

- Unlicense. This is the choice of mw2fcitx and might change in the future.

### Generated Minecraft dictionary

- CC BY-NC-SA 3.0 according to <https://zh.minecraft.wiki/w/Minecraft_Wiki:著作权>
