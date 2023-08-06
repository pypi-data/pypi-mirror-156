# QrTransfer

## What is QrTransfer?

QrTransfer trys to make it easy to transfer files with display devices only, no network available.

## Install

Install module from PyPI:
```sh
pip install QrCodeTransfer
```

## TODO

- [x] add command channel. `> command line`
  - [ ] 命令协商wait的时间，截屏的大小等
- [ ] receiver: add new threads to processing QR scanning, and wait quit signal in console.
- [ ] 尝试更高效的传输方式，压缩，qr的版本（iqr？），屏幕显示qr的数量
- [ ] 性能优化
  - [ ] sender：生成的qr图片保存在内存中
