# aoirint_hg100rclient

CATV回線用インターネットモデムHUMAX HG100R-02JGをHTTP API経由で操作するための非公式パッケージ。

```shell
pip3 install aoirint-hg100rclient
```

## Usage

### 認証情報の保存

```shell
hg100r login
```

### 認証情報の削除

```shell
hg100r logout
```

### WAN側IPv4アドレスの取得

```shell
hg100r wanipv4
```

WAN未接続時は`0.0.0.0`を返却。

### モデム再起動

```shell
hg100r reboot
```
