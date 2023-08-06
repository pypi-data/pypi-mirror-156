from ..interface.mdc_gateway_base_define import EMarketDataType


class market_service(object):
    def __init__(self):
       pass
    # ************************************处理数据订阅************************************
    # 处理订阅的股票Tick数据，mdStock格式为json格式
    # 订阅的证券类型为ESecurityType.StockType
    def onSubscribe_StockType_MD_TICK(self, mdStock):
        pass

    # 处理订阅的指数Tick数据，mdIndex格式为json格式
    # 订阅的证券类型为ESecurityType.IndexType
    def onSubscribe_IndexType_MD_TICK(self, mdIndex):
        pass
        # print(mdIndex)

    # 处理订阅的债券Tick数据，mdBond格式为json格式
    # 订阅的证券类型为ESecurityType.BondType
    def onSubscribe_BondType_MD_TICK(self, mdBond):
        pass
        # print(mdBond)

    # 处理订阅的基金Tick数据，mdFund格式为json格式
    # 订阅的证券类型为ESecurityType.FundType
    def onSubscribe_FundType_MD_TICK(self, mdFund):
        pass
        # print(mdFund)

    # 处理订阅的期权Tick数据，mdOption格式为json格式
    # 订阅的证券类型为ESecurityType.OptionType
    def onSubscribe_OptionType_MD_TICK(self, mdOption):
        pass
        # print(mdOption)

    # 处理订阅的期货Tick数据，mdFuture格式为json格式
    # 订阅的证券类型为ESecurityType.OptionType
    def onSubscribe_FuturesType_MD_TICK(self, mdFuture):
        pass
        # print(mdFuture)

    # 处理订阅的逐笔成交，marketdatajson格式为json格式
    # 订阅的证券类型为ESecurityType.MD_TRANSACTION
    # 处理订阅的逐笔委托，格式为json格式
    # 订阅的证券类型为ESecurityType.MD_ORDER
    def onSubscribe_MD_TRANSACTION_and_MD_ORDER(self, marketdatajson):
        if marketdatajson["marketDataType"] == EMarketDataType.MD_TRANSACTION:  # 逐笔成交
            mdtransaction = marketdatajson["mdTransaction"]
            pass
            # print(mdtransaction)
        elif marketdatajson["marketDataType"] == EMarketDataType.MD_ORDER:  # 逐笔委托
            mdorder = marketdatajson["mdOrder"]
            pass
            # print(mdorder)
        # print(marketdatajsons)

    # 处理订阅的K线指标模型，marketdatajson格式为json格式
    # 订阅的数据类型为EMarketDataType.MD_KLINE_15S 返回#15秒钟K线
    # 订阅的数据类型为EMarketDataType.MD_KLINE_1MIN 返回#1分钟K线
    # 订阅的数据类型为EMarketDataType.MD_KLINE_5MIN 返回#5分钟K线
    # 订阅的数据类型为EMarketDataType.MD_KLINE_15MIN 返回#15分钟K线
    # 订阅的数据类型为EMarketDataType.MD_KLINE_30MIN 返回#30分钟K线
    # 订阅的数据类型为EMarketDataType.MD_KLINE_60MIN 返回#60分钟K线
    # 订阅的数据类型为EMarketDataType.MD_KLINE_1D 返回#日K线
    def onSubscribe_MD_KLINE(self, marketdatajson):
        if marketdatajson["marketDataType"] == EMarketDataType.MD_KLINE_15S:  # 15秒钟K线
            mdKLine = marketdatajson["mdKLine"]
            pass
            # print(mdKLine)
        elif marketdatajson["marketDataType"] == EMarketDataType.MD_KLINE_1MIN:  # 1分钟K线
            mdKLine = marketdatajson["mdKLine"]
            pass
            # print(mdKLine)
        elif marketdatajson["marketDataType"] == EMarketDataType.MD_KLINE_5MIN:  # 5分钟K线
            mdKLine = marketdatajson["mdKLine"]
            pass
            # print(mdKLine)
        elif marketdatajson["marketDataType"] == EMarketDataType.MD_KLINE_15MIN:  # 15分钟K线
            mdKLine = marketdatajson["mdKLine"]
            pass
            # print(mdKLine)
        elif marketdatajson["marketDataType"] == EMarketDataType.MD_KLINE_30MIN:  # 30分钟K线
            mdKLine = marketdatajson["mdKLine"]
            pass
            # print(mdKLine)
        elif marketdatajson["marketDataType"] == EMarketDataType.MD_KLINE_60MIN:  # 60分钟K线
            mdKLine = marketdatajson["mdKLine"]
            pass
            # print(mdKLine)
        elif marketdatajson["marketDataType"] == EMarketDataType.MD_KLINE_1D:  # 日K线
            mdKLine = marketdatajson["mdKLine"]
            pass
            # print(mdKLine)

        # print(marketdatajson)

    # 处理订阅的资金流向数据，mdFundFlowAnalysis格式为json格式
    # 订阅的证券类型为ESecurityType.AD_FUND_FLOW_ANALYSIS
    def onSubscribe_AD_FUND_FLOW_ANALYSIS(self, mdFundFlowAnalysis):
        pass
        # print(mdFundFlowAnalysis)

    # 处理订阅的融券通数据，mdSecurityLending格式为json格式
    # 订阅的证券类型为ESecurityType.MD_SECURITY_LENDING
    def onSubscribe_MD_SECURITY_LENDING(self, mdSecurityLending):
        pass
        # print(mdSecurityLending)

    # ************************************处理回放数据************************************
    # 处理回放的股票Tick数据，mdStock格式为json格式
    # 回放的证券类型为ESecurityType.StockType
    def onPlayback_StockType_MD_TICK(self, mdStock):
        pass
        # print(mdStock)

    # 处理回放的指数Tick数据，mdIndex格式为json格式
    # 回放的证券类型为ESecurityType.IndexType
    def onPlayback_IndexType_MD_TICK(self, mdIndex):
        pass
        # print(mdIndex)

    # 处理回放的债券Tick数据，mdBond格式为json格式
    # 回放的证券类型为ESecurityType.BondType
    def onPlayback_BondType_MD_TICK(self, mdBond):
        pass
        # print(mdBond)

    # 处理回放的基金Tick数据，mdFund格式为json格式
    # 回放的证券类型为ESecurityType.FundType
    def onPlayback_FundType_MD_TICK(self, mdFund):
        pass
        # print(mdFund)

    # 处理回放的期权Tick数据，mdOption格式为json格式
    # 回放的证券类型为ESecurityType.OptionType
    def onPlayback_OptionType_MD_TICK(self, mdOption):
        pass
        # print(mdOption)

    # 处理回放的期货Tick数据，mdFuture格式为json格式
    # 回放的证券类型为ESecurityType.OptionType
    def onPlayback_FuturesType_MD_TICK(self, mdFuture):
        pass
        # print(mdFuture)

    # 处理回放的逐笔成交，marketdatajson格式为json格式
    # 回放的证券类型为ESecurityType.MD_TRANSACTION
    # 处理回放的逐笔委托，格式为json格式
    # 回放的证券类型为ESecurityType.MD_ORDER
    def onPlayback_MD_TRANSACTION_and_MD_ORDER(self, marketdatajson):
        if marketdatajson["marketDataType"] == EMarketDataType.MD_TRANSACTION:  # 逐笔成交
            mdtransaction = marketdatajson["mdTransaction"]
            pass
            # print(mdtransaction)
        elif marketdatajson["marketDataType"] == EMarketDataType.MD_ORDER:  # 逐笔委托
            mdorder = marketdatajson["mdOrder"]
            pass
            # print(mdorder)
        # print(marketdatajsons)

    # 处理回放的K线指标模型，marketdatajson格式为json格式
    # 回放的数据类型为EMarketDataType.MD_KLINE_15S 返回#15秒钟K线
    # 回放的数据类型为EMarketDataType.MD_KLINE_1MIN 返回#1分钟K线
    # 回放的数据类型为EMarketDataType.MD_KLINE_5MIN 返回#5分钟K线
    # 回放的数据类型为EMarketDataType.MD_KLINE_15MIN 返回#15分钟K线
    # 回放的数据类型为EMarketDataType.MD_KLINE_30MIN 返回#30分钟K线
    # 回放的数据类型为EMarketDataType.MD_KLINE_60MIN 返回#60分钟K线
    # 回放的数据类型为EMarketDataType.MD_KLINE_1D 返回#日K线
    def onPlayback_MD_KLINE(self, marketdatajson):
        if marketdatajson["marketDataType"] == EMarketDataType.MD_KLINE_15S:  # 15秒钟K线
            mdKLine = marketdatajson["mdKLine"]
            pass
            # print(mdKLine)
        elif marketdatajson["marketDataType"] == EMarketDataType.MD_KLINE_1MIN:  # 1分钟K线
            mdKLine = marketdatajson["mdKLine"]
            pass
            # print(mdKLine)
        elif marketdatajson["marketDataType"] == EMarketDataType.MD_KLINE_5MIN:  # 5分钟K线
            mdKLine = marketdatajson["mdKLine"]
            pass
            # print(mdKLine)
        elif marketdatajson["marketDataType"] == EMarketDataType.MD_KLINE_15MIN:  # 15分钟K线
            mdKLine = marketdatajson["mdKLine"]
            pass
            # print(mdKLine)
        elif marketdatajson["marketDataType"] == EMarketDataType.MD_KLINE_30MIN:  # 30分钟K线
            mdKLine = marketdatajson["mdKLine"]
            pass
            # print(mdKLine)
        elif marketdatajson["marketDataType"] == EMarketDataType.MD_KLINE_60MIN:  # 60分钟K线
            mdKLine = marketdatajson["mdKLine"]
            pass
            # print(mdKLine)
        elif marketdatajson["marketDataType"] == EMarketDataType.MD_KLINE_1D:  # 日K线
            mdKLine = marketdatajson["mdKLine"]
            pass
            # print(mdKLine)

        # print(marketdatajson)

    # 处理回放的资金流向数据，mdFundFlowAnalysis格式为json格式
    # 回放的证券类型为ESecurityType.AD_FUND_FLOW_ANALYSIS
    def onPlayback_AD_FUND_FLOW_ANALYSIS(self, mdFundFlowAnalysis):
        pass
        # print(mdFundFlowAnalysis)

    # 处理回放的融券通数据，mdSecurityLending格式为json格式
    # 回放的证券类型为ESecurityType.MD_SECURITY_LENDING
    def onPlayback_MD_SECURITY_LENDING(self, mdSecurityLending):
        pass
        # print(mdSecurityLending)

    # 处理回放的状态，status格式为string格式
    def onPlaybackStatus(self, status):
        pass
        # print(status)

    # 处理回放请求返回结果，response格式为string格式
    def onPlaybackResponse(self, response):
        pass
        # print(response)

    # 处理回放控制请求返回结果，response格式为string格式
    def onPlaybackControlResponse(self, response):
        pass
        # print(response)

    # ************************************处理查询请求返回结果************************************
    # 处理查询历史上所有的指定证券的基础信息 query_mdcontant_by_type()的返回结果，queryresponse格式为list[json]
    # 处理查询今日最新的指定证券的基础信息 query_last_mdcontant_by_type()的返回结果，queryresponse格式为list[json]
    # 处理查询历史上所有的指定证券的基础信息 query_mdcontant_by_id()的返回结果，queryresponse格式为list[json]
    # 处理查询今日最新的指定证券的基础信息 query_last_mdcontant_by_id()的返回结果，queryresponse格式为list[json]
    # 处理查询指定证券的ETF的基础信息 query_ETFinfo()的返回结果，queryresponse格式为list[json]
    # 处理查询指定证券的最新一条Tick数据 query_last_mdtick()的返回结果，queryresponse格式为list[json]
    def onQueryResponse(self, queryresponse):
        pass
        # for resonse in iter(queryresponse):
        #     # response格式为json格式
        #     print(resonse)

