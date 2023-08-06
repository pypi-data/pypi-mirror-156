# aoirint_hg100rclient

CATV回線用インターネットモデムHUMAX HG100R-02JGをHTTP API経由で操作するための非公式パッケージ。

## Usage

### WAN側IPv4アドレスの取得

```shell
hg100r wanipv4
```

WAN未接続時は`0.0.0.0`を返却。

### モデム再起動

```shell
hg100r reboot
```
