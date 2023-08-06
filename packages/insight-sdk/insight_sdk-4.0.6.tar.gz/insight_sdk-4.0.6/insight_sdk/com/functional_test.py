﻿#!/usr/bin/python3
# -*- coding: utf-8 -*-


from com.interface.mdc_gateway_base_define import ESubscribeActionType, ESecurityIDSource, ESecurityType, \
    EMarketDataType, MDPlaybackExrightsType
from com.insight import common, query, playback, subscribe
from com.insight.market_service import market_service


class insightmarketservice(market_service):
    def __init__(self):
        pass

    # ************************************处理数据订阅************************************
    # 处理订阅的股票Tick数据，mdStock格式为json格式
    # 订阅的证券类型为ESecurityType.StockType
    def onSubscribe_StockType_MD_TICK(self, mdStock):
        print(mdStock)
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
        for resonse in iter(queryresponse):
            # response格式为json格式
            print(resonse)


# ************************************用户登录************************************
# 登陆
# user 用户名
# password 密码
def login():
    markets = insightmarketservice()
    # 登陆前 初始化
    user = ""
    password = ""
    # result格式为string格式
    result = common.login(markets, user, password)
    print(result)


# 配置日志打开
# open_trace trace日志开关     True为打开日志False关闭日志
# open_file_log  本地file日志开关     True为打开日志False关闭日志
# open_cout_log  控制台日志开关     True为打开日志False关闭日志
def config(open_trace=True, open_file_log=True, open_cout_log=True):
    common.config(open_trace, open_file_log, open_cout_log)


# ************************************数据订阅************************************
# 根据证券数据来源订阅行情数据,由三部分确定行情数据
# 行情源(SecurityIdSource):XSHG(沪市)|XSHE(深市)|...
# 证券类型(SecurityType):BondType(债)|StockType(股)|FundType(基)|IndexType(指)|OptionType(期权)|...
# 数据类型(MarketDataTypes):MD_TICK(快照)|MD_TRANSACTION(逐笔成交)|MD_ORDER(逐笔委托)|...
# 异步接口，返回函数在functional_test.py
# 结果返回 onSubscribe_StockType_MD_TICK 处理订阅的股票Tick数据
# 结果返回 onSubscribe_IndexType_MD_TICK 处理订阅的指数Tick数据
# 结果返回 onSubscribe_BondType_MD_TICK 处理订阅的债券Tick数据
# 结果返回 onSubscribe_FundType_MD_TICK 处理订阅的基金Tick数据
# 结果返回 onSubscribe_OptionType_MD_TICK 处理订阅的期权Tick数据
# 结果返回 onSubscribe_FuturesType_MD_TICK 处理订阅的期货Tick数据
# 结果返回 onSubscribe_MD_TRANSACTION_and_MD_ORDER 处理订阅的逐笔成交和逐笔委托的数据
# 结果返回 onSubscribe_MD_KLINE 处理订阅的K线指标模型数据
# 结果返回 onSubscribe_AD_FUND_FLOW_ANALYSIS 处理订阅的资金流向数据
# 结果返回 onSubscribe_MD_SECURITY_LENDING 处理订阅的融券通数据
def subscribe_by_type():
    # element
    # params1: ESecurityIDSource枚举值 --行情源
    # params2: ESecurityType的枚举值 --证券类型
    # params3: EMarketDataType的枚举值集合 --数据类型
    datatype = ESubscribeActionType.COVERAGE
    marketdatatypes = []
    marketdatatype = {"ESecurityIDSource": ESecurityIDSource.XSHG, "ESecurityType": ESecurityType.StockType,
                      "EMarketDataType": EMarketDataType.MD_SECURITY_LENDING}
    marketdatatypes.append(marketdatatype)
    marketdatatype1 = {"ESecurityIDSource": ESecurityIDSource.XSHE, "ESecurityType": ESecurityType.StockType,
                       "EMarketDataType": EMarketDataType.MD_TICK}
    marketdatatypes.append(marketdatatype1)

    subscribe.subscribe_by_type(marketdatatypes, datatype)


# 根据证券ID来源订阅行情数据
# 异步接口，返回函数在functional_test.py
# 结果返回 onSubscribe_StockType_MD_TICK 处理订阅的股票Tick数据
# 结果返回 onSubscribe_IndexType_MD_TICK 处理订阅的指数Tick数据
# 结果返回 onSubscribe_BondType_MD_TICK 处理订阅的债券Tick数据
# 结果返回 onSubscribe_FundType_MD_TICK 处理订阅的基金Tick数据
# 结果返回 onSubscribe_OptionType_MD_TICK 处理订阅的期权Tick数据
# 结果返回 onSubscribe_FuturesType_MD_TICK 处理订阅的期货Tick数据
# 结果返回 onSubscribe_MD_TRANSACTION_and_MD_ORDER 处理订阅的逐笔成交和逐笔委托的数据
# 结果返回 onSubscribe_MD_KLINE 处理订阅的K线指标模型数据
# 结果返回 onSubscribe_AD_FUND_FLOW_ANALYSIS 处理订阅的资金流向数据
# 结果返回 onSubscribe_MD_SECURITY_LENDING 处理订阅的融券通数据
def subscribe_by_id():
    # params1:HTSCSecurityID华泰内部证券标string --证券代码
    # params2: EMarketDataType的枚举值集合 --数据类型
    datatype = ESubscribeActionType.COVERAGE
    HTSCSecurityIDs = []
    HTSCSecurityID = {"HTSCSecurityID": "002371.SZ", "EMarketDataType": EMarketDataType.MD_TICK}
    HTSCSecurityIDs.append(HTSCSecurityID)

    HTSCSecurityID1 = {"HTSCSecurityID": "002714.SZ", "EMarketDataType": EMarketDataType.MD_TICK}
    HTSCSecurityIDs.append(HTSCSecurityID1)
    subscribe.subscribe_by_id(HTSCSecurityIDs, datatype)


# ************************************数据查询************************************
# 查询findata数据，返回结果list[json]
# 同步接口，返回结果为result，格式为list[json]
def query_fin_info():
    # params1:Hquery_type  int
    # params2:params  dict{}
    query_type = 1102010003
    params = {"HTSC_SECURITY_ID": "510050.SH", "START_DATE": "20210101", "END_DATE": "20210107"}
    # query_type = 1002010001
    # params = {"HTSC_SECURITY_ID": "601688.SH", "START_DATE": "20191211", "END_DATE": "20201010"}
    # query_type = 1002070003
    # params = {"HTSC_SECURITY_ID": "600498.SH", "START_TIME": "20200101000000", "END_TIME": "20210107000000", "EXRIGHTS_TYPE": "NoExrights", "EMD_PERIOD_TYPE":"Period1D"}
    result = query.query_fin_info(query_type, params)
    if isinstance(result, list):
        for response in iter(result):
            print(response)
    else:
        print(result)


# 查询历史上所有的指定证券的基础信息
# params:securityIdSource 为市场ESecurityIDSource 枚举值;securityType 为 ESecurityType枚举值
# 异步接口，返回函数在functional_test.py
# 结果返回在onQueryResponse函数
def query_mdcontant_by_type():
    # params:security_idsource 为 ESecurityIDSource枚举值
    # params:security_type 为 ESecurityType枚举值
    # 沪市 股票
    idsource_and_types = []
    security_idsource = ESecurityIDSource.XSHG
    security_type = ESecurityType.StockType
    idsource_and_type = {"ESecurityIDSource": security_idsource, "ESecurityType": security_type}
    idsource_and_types.append(idsource_and_type)
    security_idsource1 = ESecurityIDSource.XSHE
    security_type1 = ESecurityType.IndexType
    idsource_and_type1 = {"ESecurityIDSource": security_idsource1, "ESecurityType": security_type1}
    idsource_and_types.append(idsource_and_type1)

    query.query_basicInfo_by_type(idsource_and_types, False)


# 查询今日最新的指定证券的基础信息
# params:securityIdSource 为市场ESecurityIDSource 枚举值;securityType 为 ESecurityType枚举值
# 异步接口，返回函数在functional_test.py
# 结果返回在onQueryResponse函数
def query_last_mdcontant_by_type():
    # 按市场查询
    # 沪市 股票

    idsource_and_types = []
    security_idsource = ESecurityIDSource.XSHG
    security_type = ESecurityType.StockType
    idsource_and_type = {"ESecurityIDSource": security_idsource, "ESecurityType": security_type}
    idsource_and_types.append(idsource_and_type)
    security_idsource1 = ESecurityIDSource.XSHE
    security_type1 = ESecurityType.IndexType
    idsource_and_type1 = {"ESecurityIDSource": security_idsource1, "ESecurityType": security_type1}
    idsource_and_types.append(idsource_and_type1)

    query.query_basicInfo_by_type(idsource_and_types, True)


# 查询历史上所有的指定证券的基础信息 -- 结果返回在onQueryResponse
# param:HTSCSecurityID华泰内部证券标string --证券代码
# params:list[HTSCSecurityID]
# 异步接口，返回函数在functional_test.py
# 结果返回在onQueryResponse函数
def query_mdcontant_by_id():
    # params:security_idsource 为 ESecurityIDSource枚举值
    # params:security_type 为 ESecurityType枚举值
    # params:security_id_list 为 标的集合
    security_id_list = ["601688.SH", "002714.SZ"]  # 置空表示不额外查询某些标的
    query.query_basicInfo_by_id(security_id_list, False)


# 查询今日最新的指定证券的基础信息 -- 结果返回在onQueryResponse
# param:HTSCSecurityID华泰内部证券标string --证券代码
# params:list[HTSCSecurityID]
# 异步接口，返回函数在functional_test.py
# 结果返回在onQueryResponse函数
def query_last_mdcontant_by_id():
    # 按市场查询
    # 沪市 股票

    # params:security_id_list 为 标的集合
    security_id_list = ["601688.SH"]  # 置空表示不额外查询某些标的
    query.query_basicInfo_by_id(security_id_list, True)


# 查询指定证券的ETF的基础信息 -- 结果返回在onQueryResponse
# params:securityIdSource 为市场ESecurityIDSource 枚举值;securityType 为 ESecurityType枚举值
# 异步接口，返回函数在functional_test.py
# 结果返回在onQueryResponse函数
def query_ETFinfo():
    # params:securityIDSource 为 ESecurityIDSource枚举值
    # params:securityType 为 ESecurityType枚举值
    query.query_ETFinfo(ESecurityIDSource.XSHG, ESecurityType.FundType)


# 查询指定证券的最新一条Tick数据 --  结果返回在onQueryResponse
# params:securityIdSource 为市场ESecurityIDSource 枚举值;securityType 为 ESecurityType枚举值
# 异步接口，返回函数在functional_test.py
# 结果返回在onQueryResponse函数
def query_last_mdtick():
    # params:security_idsource 为 ESecurityIDSource枚举值
    # params:security_type 为 ESecurityType枚举值
    # 沪市 股票
    query.query_last_tick_by_type(ESecurityIDSource.XSHG, ESecurityType.StockType)


# ************************************回放************************************
# 回放接口 (注意：securitylist 和 securityIdList取并集!!!)
# 回放限制
# 对于回放而言，时间限制由股票只数和天数的乘积决定，要求 回放只数 × 回放天数 × 证券权重 ≤ 450，交易时间段内回放功能 乘积<=200。
# Tick/Transaction/Order回放时间范围限制是30天，每支证券权重为1，即可以回放15只股票30天以内的数据或450支股票1天内数据。
# 日K数据回放时间范围限制是365天，每支证券权重为0.005。
# 分钟K线数据回放时间范围限制是90天，每支证券权重0.05。
# 数据最早可以回放到 2017年1月2日
# 异步接口，返回函数在functional_test.py
# 结果返回 onPlayback_StockType_MD_TICK 处理回放的股票Tick数据
# 结果返回 onPlayback_IndexType_MD_TICK 处理回放的指数Tick数据
# 结果返回 onPlayback_BondType_MD_TICK 处理回放的债券Tick数据
# 结果返回 onPlayback_FundType_MD_TICK 处理回放的基金Tick数据
# 结果返回 onPlayback_OptionType_MD_TICK 处理回放的期权Tick数据
# 结果返回 onPlayback_FuturesType_MD_TICK 处理回放的期货Tick数据
# 结果返回 onPlayback_MD_TRANSACTION_and_MD_ORDER 处理回放的逐笔成交和逐笔委托的数据
# 结果返回 onPlayback_MD_KLINE 处理回放的K线指标模型数据
# 结果返回 onPlayback_AD_FUND_FLOW_ANALYSIS 处理回放的资金流向数据
# 结果返回 onPlayback_MD_SECURITY_LENDING 处理回放的融券通数据
def play_back():
    # 回放数据类型 EMarketDataType 详情请参阅 数据手册EMarketDataType
    # 示例：MD_TICK
    marketdata_type = EMarketDataType.MD_TICK

    # 是否复权 EPlaybackTaskStatus 详情请参阅 数据手册EPlaybackTaskStatus
    # 示例： 不复权
    exrights_type = MDPlaybackExrightsType.DEFAULT_EXRIGHTS_TYPE

    # 回放时间起：start_time 注意格式
    # 回放时间止：stop_time  注意格式
    # 回放时间起止间隔 不超过上述 时间范围限制
    start_time = "20220420090000"
    stop_time = "20220420150000"

    htscsecurityID_and_types = []
    marketdata_type = EMarketDataType.MD_TICK
    htscsecurityID_and_type = {"HTSCSecurityID": "601688.SH", "EMarketDataType": marketdata_type}
    htscsecurityID_and_types.append(htscsecurityID_and_type)
    marketdata_type1 = EMarketDataType.MD_TICK
    htscsecurityID_and_type1 = {"HTSCSecurityID": "000014.SZ", "EMarketDataType": marketdata_type1}
    htscsecurityID_and_types.append(htscsecurityID_and_type1)

    # 特别注意！！！！
    # security_id_list 注意回放限制
    playback.playback(htscsecurityID_and_types, exrights_type, start_time, stop_time)


# 盘中回放接口 --securitylist 和 securityIdList取并集
# Can only query data for one day
# 异步接口，返回函数在functional_test.py
# 结果返回 onPlayback_StockType_MD_TICK 处理回放的股票Tick数据
# 结果返回 onPlayback_IndexType_MD_TICK 处理回放的指数Tick数据
# 结果返回 onPlayback_BondType_MD_TICK 处理回放的债券Tick数据
# 结果返回 onPlayback_FundType_MD_TICK 处理回放的基金Tick数据
# 结果返回 onPlayback_OptionType_MD_TICK 处理回放的期权Tick数据
# 结果返回 onPlayback_FuturesType_MD_TICK 处理回放的期货Tick数据
# 结果返回 onPlayback_MD_TRANSACTION_and_MD_ORDER 处理回放的逐笔成交和逐笔委托的数据
# 结果返回 onPlayback_MD_KLINE 处理回放的K线指标模型数据
# 结果返回 onPlayback_AD_FUND_FLOW_ANALYSIS 处理回放的资金流向数据
# 结果返回 onPlayback_MD_SECURITY_LENDING 处理回放的融券通数据
def play_back_oneday():
    # 回放数据类型 EMarketDataType 详情请参阅 数据手册EMarketDataType
    # 示例：MD_TICK

    # 是否复权 EPlaybackTaskStatus 详情请参阅 数据手册EPlaybackTaskStatus
    # 示例： 不复权
    exrights_type = MDPlaybackExrightsType.DEFAULT_EXRIGHTS_TYPE
    htscsecurityID_and_types = []
    marketdata_type = EMarketDataType.MD_TICK
    htscsecurityID_and_type = {"HTSCSecurityID": "601688.SH", "EMarketDataType": marketdata_type}
    htscsecurityID_and_types.append(htscsecurityID_and_type)
    marketdata_type1 = EMarketDataType.MD_TICK
    htscsecurityID_and_type1 = {"HTSCSecurityID": "000014.SZ", "EMarketDataType": marketdata_type1}
    htscsecurityID_and_types.append(htscsecurityID_and_type1)

    # 特别注意！！！！
    # security_id_list 注意回放限制
    playback.play_back_oneday(htscsecurityID_and_types, exrights_type)


# 获取当前版本号
def get_version():
    print(common.get_version())


# 释放资源
def fini():
    common.fini()


# 使用指导：登陆 -> 订阅/查询/回放 -> 退出
def main(markets=None):

    # 登陆部分调用
    get_version()
    login()
    config(False, False, False)
    # 订阅部分接口调用

    subscribe_by_type()
    # subscribe_by_id()
    # 查询部分接口调用
    # query_fin_info()
    # query_mdcontant_by_type()dd
    # query_last_mdcontant_by_type()
    # query_mdcontant_by_id()
    # query_last_mdcontant_by_id()

    #query_ETFinfo()
    # query_last_mdtick()
    # 回放部分接口调用
    # play_back()
    # play_back_oneday()
    # 退出释放资源
    fini()


if __name__ == "__main__":
    # insight SDK 采用网络异步方式 ---- 请求访问和数据返回 异步交互
    # 这里是 functional_test.py 是 登陆、订阅、查询、回测（也称回放）操作部分
    # 以订阅为例： functional_test.py 中，执行登陆->订阅,操作结束后,数据通过 data_handle.py中 OnRecvMarkertData()的成员方法回调返回（回调详情请参照使用手册）
    main()
