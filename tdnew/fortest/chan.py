# -*- coding: utf-8 -*-
__author__ = 'xujh'

import matplotlib.pyplot as plt
import os
import pandas as pd
import datetime
import matplotlib.dates as dt
from matplotlib.lines import Line2D
from matplotlib.dates import *
import math
import nanotime
import numba

from pylab import *

mpl.rcParams['font.sans-serif'] = ['SimHei']

st = nanotime.now()
hqdatadir = 'D:\TdxW_HuaTai\T0002\export2'
code = '999999'
# code = '399006'
filepath = os.path.join(hqdatadir, (code + '.txt'))
# if not os.path.exists(filepath):
#     logger.critical("filepath %s does not exist", filepath)
#     raise RuntimeError, 'filepath does not exist'

rnames = ['d', 't', 'open', 'high', 'low', 'close', 'volume', 'amt']
df5mKline = pd.read_table(filepath,
                          engine='python', sep=',',
                          encoding='gbk',
                          names=rnames,
                          parse_dates={'time': ['d', 't']},
                          index_col='time',
                          skiprows=2,
                          skipfooter=1)
print ('load txt data cost:%d' % (nanotime.now() - st).milliseconds())


class Base(object):
    def __init__(self):
        self.idx = 0

    def __str__(self):
        return str(self.__dict__) + '\n'

    def __repr__(self):
        return str(self)


class Kline(Base):
    def __init__(self, **kwargs):
        super(Kline, self).__init__()
        # shape 用于区分是顶分型还是底分型
        self.high = kwargs['high']
        self.low = kwargs['low']
        self.shape = kwargs['shape'] if 'shape' in kwargs else 'un'


class Pen(Base):
    def __init__(self, **kwargs):
        super(Pen, self).__init__()
        # loc在标准k线列表中所处的index，value顶点或者底点的值，shape顶分型还是底分型
        self.loc = kwargs['loc']
        self.value = kwargs['value']
        self.shape = kwargs['shape'] if 'shape' in kwargs else 'un'


class Seq(Base):
    def __init__(self, **kwargs):
        super(Pen, self).__init__()
        self.bloc = kwargs['bloc']
        self.eloc = kwargs['eloc']
        self.bvalue = kwargs['bvalue']
        self.evalue = kwargs['evalue']
        self.high = kwargs['high'] if 'high' in kwargs else 'un'
        self.low = kwargs['low'] if 'low' in kwargs else 'un'


class Toolkit(object):
    def __init__(self):
        pass

    # 是否存在包含关系
    @staticmethod
    def isContain(prekline, curkline):
        # 向左包含 n+1包含n
        if curkline.high >= prekline.high and curkline.low <= prekline.low:
            return True
        # 向右包含 n包含n+1
        elif curkline.high <= prekline.high and curkline.low >= prekline.low:
            return True
        else:
            return False


    # 判断是上升趋势还是下降趋势,True为上升趋势，False为下降趋势
    @staticmethod
    def isUp(line1, line2):
        if line2.high >= line1.high and line2.low >= line1.low:
            return True
        else:
            return False


    @staticmethod
    def getShape(line1, line2, line3):
        # 顶分型
        if line2.high > line1.high \
                and line2.high > line3.high \
                and line2.low > line1.low \
                and line2.low > line3.low:
            return 'u'
        # 底分型
        elif line2.high < line1.high \
                and line2.high < line3.high \
                and line2.low < line1.low \
                and line2.low < line3.low:
            return 'd'
        # 未知情况
        else:
            return 'na'


    @staticmethod
    # @profile
    def append(list, dict_value):
        dict_value.idx = len(list)
        list.append(dict_value)
        # # 用'un'填补df中没有的字段，否则会出现插入错误
        # df_columns_set = set(list.columns.values)
        # dict_value_set = set(dict_value.keys())
        #
        # andSet = df_columns_set & dict_value_set
        # difSet = df_columns_set - dict_value_set
        #
        # # 从dict_value中取df对应有的列和值，df缺失的列默认用'un'替代
        # value_to_set = dict({k: dict_value[k] for k in andSet},
        #                     **{k: 'un' for k in difSet})
        #
        # list.loc[list.shape[0]] = value_to_set


    @staticmethod
    # @profile
    def procContain(list, isUp, newkline):
        if len(list) < 1 or not Toolkit.isContain(list[-1], newkline):
            Toolkit.append(list, newkline)
        else:
            # 高点取高值，低点也取高值，简单的说就是“上升取高高”
            if isUp:
                newkline.high = max(list[-1].high, newkline.high)
                newkline.low = max(list[-1].low, newkline.low)
            # 高点取低值，低点也取低值，简单的说就是“下降取低低”
            else:
                newkline.high = min(list[-1].high, newkline.high)
                newkline.low = min(list[-1].low, newkline.low)
            # 处理完包含关系后，将前一个删除，只保留最终处理完的结果
            list.pop()
            # 递归处理包含关系，有可能出现处理包含之后的元素和之前的元素还存在包含关系
            return Toolkit.procContain(list, isUp, newkline)


    # 方向（属于向上笔还是向下笔）
    @staticmethod
    def getDirect(pen_start, pen_end):
        # 向上笔
        if pen_start['value'] < pen_end['value']:
            return 'u'
        # 向下笔
        elif pen_start['value'] > pen_end['value']:
            return 'd'
        # 位置情况
        return 'na'


    @staticmethod
    def LineBreakByPen(dfPen, ):
        pass


    # 获取subDf中形态为顶分型的最高点
    @staticmethod
    # @profile
    def getUpHighPoint(subList):
        upSubList = [x for x in subList if x.shape == 'u']
        return max(upSubList, key=lambda x: x.high) if upSubList else None


    # 获取subDf中形态为底分型的最低点
    @staticmethod
    # @profile
    def getDownLowPoint(subList):
        downSubList = [x for x in subList if x.shape == 'd']
        return min(downSubList, key=lambda x: x.low) if downSubList else None


class Chan(object):
    def __init__(self, isUp):
        self._isUp = isUp

        #处理包含关系后的标准k线list
        self._KlineList = []

        #笔的端点list
        self._PenList = []

        # 特征序列
        self._SeqList = []

        # 线段
        self._LineList = []

        self._shapeVariableSet = ['na', 'u', 'd']
        self._penBeginSearch = 0

    # def get_klinelist(self):
    #     return self._df
    #
    # def getPen(self):
    #     return self._pen
    #
    # def getSequence(self):
    #     return self._sequence

    # @profile
    def procKlineContain(self, list, newkline):
        if len(list) < 2:
            Toolkit.procContain(list, self._isUp, newkline)
        else:
            Toolkit.procContain(list, Toolkit.isUp(list[-2], list[-1]), newkline)

    # @profile
    def onNewKline(self, newkline_):
        newkline = Kline(high = newkline_.high, low = newkline_.low)
        self.procKlineContain(self._KlineList, newkline)
        self.procShape()

        self.procPen()

        # # 有新笔生成才需要进行线段的处理
        # if self.procPen():
        #     self.procLine()

    def procLine(self):
        # 生成的最后一笔是会变的
        # 笔的方向可以通过终点的类型来判断，如果是'u'则是向上笔，如果是'd'则是向下笔
        # 首次开始
        # 笔的数量小于3时，不可能形成线段
        if self._pen.shape[0] < 3:
            return

        if self._line.shape[0] < 2:
            if self._pen.shape[0] % 2 == 0:
                newpen = {'bloc': self._pen.iloc[-3]['loc'],
                          'bvalue': self._pen.iloc[-3]['value'],
                          'eloc': self._pen.iloc[-2]['loc'],
                          'evalue': self._pen.iloc[-2]['value'],
                          'high': max(self._pen.iloc[-3]['value'], self._pen.iloc[-2]['value']),
                          'low': min(self._pen.iloc[-3]['value'], self._pen.iloc[-2]['value'])
                          }
                self._procContain(self._sequence,
                                  True if self._pen.iloc[0, self._pen.columns.get_loc('shape')] == 'd' else False,
                                  newpen)

                # self._sequence.loc[self._sequence.shape[0]] = {'bloc': self._pen.iloc[-3]['loc'],
                #                                                'bvalue': self._pen.iloc[-3]['value'],
                #                                                'eloc': self._pen.iloc[-2]['loc'],
                #                                                'evalue': self._pen.iloc[-2]['value'],
                #                                                'high': max(self._pen.iloc[-3]['value'], self._pen.iloc[-2]['value']),
                #                                                'low': min(self._pen.iloc[-3]['value'], self._pen.iloc[-2]['value'])
                #                                                }
                # shape = self._pen.iloc[0, self._pen.columns.get_loc('shape')] == 'u'
                # #向下笔开始，笔的起点为顶分型
                # if shape == 'u':
                #     self._sequence.loc[df.shape[0]] = {'loc': 25, 'shape': 'u', 'value': 2568}
                # #向上笔开始，笔的起点为底分型
                # elif shape == 'd':
                #     pass

        else:
            pass

    # @profile
    # 返回值为True：有新笔生成，False：没有新笔生成
    def procPen(self):
        # 首次开始
        if len(self._PenList) < 2:
            dh = Toolkit.getUpHighPoint(self._KlineList)
            if dh is None:
                return False
            dl = Toolkit.getDownLowPoint(self._KlineList)
            if dl is None:
                return False
            dhLoc = dh.idx
            dlLoc = dl.idx

            if abs(dhLoc - dlLoc) >= 4:
                if dhLoc > dlLoc:
                    Toolkit.append(self._PenList, Pen(loc=dlLoc, shape=dl.shape, value=dl.low))
                    Toolkit.append(self._PenList, Pen(loc=dhLoc, shape=dh.shape, value=dh.high))
                else:
                    Toolkit.append(self._PenList, Pen(loc=dhLoc, shape=dh.shape, value=dh.high))
                    Toolkit.append(self._PenList, Pen(loc=dlLoc, shape=dl.shape, value=dl.low))
                return True
            else:
                return False
        else:
            # 前一趋势是向上时
            if self._PenList[-1].shape == 'u':
                dh = Toolkit.getUpHighPoint(self._KlineList[self._PenList[-1].loc:])
                if dh is None:
                    return False
                dhLoc = dh.idx
                if dhLoc > self._PenList[-1].loc:
                    self._PenList[-1].loc = dhLoc
                    self._PenList[-1].value = dh.high
                dl = Toolkit.getDownLowPoint(self._KlineList[dhLoc:])
                if dl is None:
                    return False
                dlLoc = dl.idx
                if abs(dlLoc - self._PenList[-1].loc) >= 4:
                    Toolkit.append(self._PenList, Pen(loc=dlLoc, shape=dl.shape, value=dl.low))
                else:
                    return False
            # 前一趋势是向下时
            else:
                dl = Toolkit.getDownLowPoint(self._KlineList[self._PenList[-1].loc:])
                if dl is None:
                    return False
                dlLoc = dl.idx
                if dlLoc > self._PenList[-1].loc:
                    self._PenList[-1].loc= dlLoc
                    self._PenList[-1].value = dl.low
                dh = Toolkit.getUpHighPoint(self._KlineList[dlLoc:])
                if dh is None:
                    return False
                dhLoc = dh.idx
                if abs(dhLoc - self._PenList[-1].loc) >= 4:
                    Toolkit.append(self._PenList, Pen(loc=dhLoc, shape=dh.shape, value=dh.high))
                    return True
                else:
                    return False

    # @profile
    def procShape(self):
        if len(self._KlineList) < 3:
            return
        for i in xrange(2, len(self._KlineList)):
            # 性能优化，只做一次推断，不重复推断
            if self._KlineList[-i].shape in self._shapeVariableSet:
                break

            self._KlineList[-i].shape = Toolkit.getShape(
                self._KlineList[-i - 1],
                self._KlineList[-i],
                self._KlineList[-i + 1])




def resample(timedelta, df):
    times = int(math.ceil(pd.Timedelta(timedelta) / (df.iloc[1].name - df.iloc[0].name)))
    newdf = pd.DataFrame(columns=df.columns)
    for i in xrange(0, df.shape[0], times):
        end = i + times
        end = end if end <= df.shape[0] else df.shape[0]
        newdf.loc[df.ix[end - 1].name] = {'high': max(df[i:i + times].high.values),
                                          'low': min(df[i:i + times].low.values)}
    return newdf


def addLineDf(ax, df, **kwargs):
    for i in xrange(df.shape[0]):
        itDf = df.ix[i]
        vline = Line2D(xdata=(i+0.5, i+0.5), ydata=(itDf['low'], itDf['high']), linewidth = 3, **kwargs)
        ax.add_line(vline)

        #标识顶/底分型
        if 'shape' in itDf:
            if itDf['shape'] == 'u':
                ax.text(i+0.5, itDf['high'], 'u', color = 'r')
            elif itDf['shape'] == 'd':
                ax.text(i+0.5, itDf['low'], 'd', color = 'g')

    ax.grid(True)
    ax.autoscale_view()

def addLine1(ax, list, **kwargs):
    for i in xrange(len(list)):
        item = list[i]
        vline = Line2D(xdata=(i + 0.5, i + 0.5), ydata=(item.low, item.high), linewidth=3, **kwargs)
        ax.add_line(vline)

        # 标识顶/底分型
        if item.shape:
            if item.shape == 'u':
                ax.text(i + 0.5, item.high, 'u', color='r')
            elif item.shape == 'd':
                ax.text(i + 0.5, item.low, 'd', color='g')

    ax.grid(True)
    ax.autoscale_view()


def addPen(ax, list, **kwargs):
    # df.iloc[int(list.iloc[0]['loc'])].high
    if len(list) < 2:
        return
    for i in xrange(len(list) - 1):
        itPen1 = list[i]
        itPen2 = list[i + 1]
        vline = Line2D(xdata=(itPen1.loc, itPen2.loc), ydata=(itPen1.value, itPen2.value), **kwargs)
        ax.add_line(vline)
        ax.text(itPen1.loc, itPen1.value, i, color='cyan', fontsize='14')
    indexLast = len(list) - 1
    ax.text(list[indexLast].loc, list[indexLast].value, indexLast, color='cyan', fontsize='14')
    ax.autoscale_view()


def addLine1_(ax, df, **kwargs):
    id1, id2 = 3, 10
    itDf1 = df.ix[id1]
    itDf2 = df.ix[id2]
    vline = Line2D(xdata=(id1 + 0.5, id2 + 0.5), ydata=(itDf1.high, itDf2['low']), color='g')
    ax.add_line(vline)
    ax.text(id2 + 0.5, itDf2['low'], '^')


def no_picture():
    st = nanotime.now()

    dft = df5mKline[['high', 'low']]
    ch = Chan(True)
    for i in xrange(dft.shape[0]):
        ch.onNewKline(dft.iloc[i])

    print ('ch cost:%d' % (nanotime.now() - st).milliseconds())

    print ch._KlineList
    print ch._PenList
    # print tw.getSequence()


def picture1():
    st = nanotime.now()
    fig, ax = plt.subplots(3, 1)
    dft = df5mKline[['high', 'low']]
    # dft = resample('30min',dft)

    ch = Chan(True)
    for i in xrange(dft.shape[0]):
        ch.onNewKline(dft.iloc[i])

    ax[0].set_title(u'原始数据')
    ax[1].set_title(u'处理包含关系并生成笔')
    ax[2].set_title(u'上一图中的笔')
    addLineDf(ax[0], dft, color='b')
    addLine1(ax[1], ch._KlineList, color='b')
    addPen(ax[1], ch._PenList, color='r')
    addPen(ax[2], ch._PenList, color='r')

    #print ch._PenList
    print ('ch cost:%d' % (nanotime.now() - st).milliseconds())
    print ch._KlineList
    print ch._PenList
    plt.show()

def picture3():
    dft = df5mKline[['high', 'low']]
    # dft = resample('30min',dft)
    ch = Chan(True)
    for i in xrange(dft.shape[0]):
        fig, ax = plt.subplots(1, 1)
        ch.onNewKline(dft.ix[i])
        addLine1(ax, ch._KlineList, color='b')
        addPen(ax, ch._PenList, color='r')
        plt.show()


def addLine2(ax, df, **kwargs):
    for i in xrange(df.shape[0]):
        itDf = df.ix[i]
        vline = Line2D(xdata=(dt.date2num(itDf.name), dt.date2num(itDf.name)), ydata=(itDf['low'], itDf.high),
                       linewidth=5, **kwargs)
        ax.add_line(vline)
        ax.autoscale_view()


def picture2():
    fig, ax = plt.subplots(2, 1)
    fig.subplots_adjust(bottom=0.2)
    dft = df5mKline[['high', 'low']]
    addLine2(ax[0], dft)

    tw = Chan(True)
    for i in xrange(dft.shape[0]):
        tw.onNewKline(dft.ix[i])

    addLine2(ax[1], tw.getdf(), color='r')

    # mondays = WeekdayLocator(MONDAY)        # major ticks on the mondays
    # alldays = MinuteLocator(interval=5)              # minor ticks on the days
    # weekFormatter = DateFormatter('%b %d')  # e.g., Jan 12
    # dayFormatter = DateFormatter('%d')      # e.g., 12
    # minuteFormatter = DateFormatter('%H:%M')

    autodates = AutoDateLocator()
    for _ax in ax:
        _ax.xaxis.set_major_locator(DayLocator())
        _ax.xaxis.set_minor_locator(MinuteLocator(interval=30))
        _ax.xaxis.set_major_formatter(DateFormatter('%m/%d'))
        _ax.xaxis.set_minor_formatter(DateFormatter('%H:%M'))
        _ax.xaxis_date()
        _ax.autoscale_view()

    plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
    plt.show()


no_picture()
#picture3()