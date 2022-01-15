# Data from `assrt.net`

## Preparations

### Download Bangumi Data

Reference Project: [`TheSagasu/SagasuSpider`](https://github.com/TheSagasu/SagasuSpider)

Please run project above, then copy `./data` folder to current folder.

### Setup Aria2

Download and install [`aria2/aria2`](https://github.com/aria2/aria2)

Run with `aria2c --conf-file aria2c.conf`

## Usage

- **NOTE:** You may need to set up an HTTP proxy with multiple IP to bypass limitations of `assrt.net`

```shell
cd assrt_spider

scrapy crawl assrt_search # Search Bangumi subject results from assrt.net
scrapy crawl assrt_download # Download searched results from assrt.net
```
