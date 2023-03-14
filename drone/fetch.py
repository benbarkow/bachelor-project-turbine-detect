from icrawler.builtin import BingImageCrawler

google_crawler = BingImageCrawler(
	feeder_threads=1,
    parser_threads=2,
    downloader_threads=4,
	storage={'root_dir': 'drone/data/yolov8'})
google_crawler.crawl(
	keyword='wind turbine', max_num=400)
google_crawler.crawl(
	keyword='windrad', max_num=400)
