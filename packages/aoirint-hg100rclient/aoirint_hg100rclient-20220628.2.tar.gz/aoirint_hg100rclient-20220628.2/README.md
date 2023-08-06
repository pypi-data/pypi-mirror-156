# aoirint_hg100rclient

CATV回線用インターネットモデムHUMAX HG100R-02JGをHTTP API経由で操作するための非公式パッケージ。

## Usage
ルータIP`192.168.0.1`、Adminパスワード`password`は適宜置換。

### WAN側IPv4アドレスの取得: hg100r_getwanipv4

```shell
hg100r_getwanipv4 http://192.168.0.1/api password
```

WAN未接続時は`0.0.0.0`を返却。

### モデム再起動: hg100r_reboot

```shell
hg100r_reboot http://192.168.0.1/api password
```
