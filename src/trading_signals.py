"""
Trading Signals Module
Generates buy/sell/short signals with multi-timeframe trend analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class TradingSignals:
    """Generate trading signals based on technical indicators and trend analysis"""
    
    def __init__(self, df):
        """
        Initialize with price data
        
        Args:
            df: DataFrame with columns: timestamp, open, high, low, close, volume
        """
        self.df = df.copy()
        self.df = self.df.sort_values('timestamp').reset_index(drop=True)
        self.calculate_all_indicators()
    
    def calculate_all_indicators(self):
        """Calculate all technical indicators"""
        # Moving Averages
        self.df['sma_20'] = self.df['close'].rolling(window=20).mean()
        self.df['sma_50'] = self.df['close'].rolling(window=50).mean()
        self.df['sma_200'] = self.df['close'].rolling(window=200).mean()
        self.df['ema_12'] = self.df['close'].ewm(span=12).mean()
        self.df['ema_26'] = self.df['close'].ewm(span=26).mean()
        
        # RSI
        delta = self.df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        self.df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        self.df['macd'] = self.df['ema_12'] - self.df['ema_26']
        self.df['macd_signal'] = self.df['macd'].ewm(span=9).mean()
        self.df['macd_histogram'] = self.df['macd'] - self.df['macd_signal']
        
        # Bollinger Bands
        self.df['bb_middle'] = self.df['close'].rolling(window=20).mean()
        bb_std = self.df['close'].rolling(window=20).std()
        self.df['bb_upper'] = self.df['bb_middle'] + (bb_std * 2)
        self.df['bb_lower'] = self.df['bb_middle'] - (bb_std * 2)
        self.df['bb_position'] = (self.df['close'] - self.df['bb_lower']) / (self.df['bb_upper'] - self.df['bb_lower'])
        
        # ATR (Average True Range) for volatility
        high_low = self.df['high'] - self.df['low']
        high_close = np.abs(self.df['high'] - self.df['close'].shift())
        low_close = np.abs(self.df['low'] - self.df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        self.df['atr'] = true_range.rolling(window=14).mean()
        
        # Volume indicators
        self.df['volume_sma'] = self.df['volume'].rolling(window=20).mean()
        self.df['volume_ratio'] = self.df['volume'] / self.df['volume_sma']
    
    def detect_trend(self, timeframe='current'):
        """
        Detect market trend
        
        Args:
            timeframe: 'short' (last 20 periods), 'medium' (last 50), 'long' (last 200), 'current' (latest)
        
        Returns:
            dict with trend info
        """
        latest = self.df.iloc[-1]
        
        if timeframe == 'current':
            # Current trend based on latest data
            ma_trend = self._check_ma_trend(latest)
            price_trend = self._check_price_trend()
            momentum = self._check_momentum(latest)
            
            # Combine signals
            bullish_signals = sum([
                ma_trend == 'bullish',
                price_trend == 'bullish',
                momentum == 'bullish',
                latest['rsi'] > 50,
                latest['macd'] > latest['macd_signal']
            ])
            
            if bullish_signals >= 4:
                trend = 'BULL MARKET'
                confidence = 'HIGH'
            elif bullish_signals >= 3:
                trend = 'BULLISH'
                confidence = 'MEDIUM'
            elif bullish_signals == 2:
                trend = 'NEUTRAL'
                confidence = 'LOW'
            elif bullish_signals == 1:
                trend = 'BEARISH'
                confidence = 'MEDIUM'
            else:
                trend = 'BEAR MARKET'
                confidence = 'HIGH'
        
        return {
            'trend': trend,
            'confidence': confidence,
            'ma_alignment': ma_trend,
            'price_action': price_trend,
            'momentum': momentum,
            'rsi': latest['rsi'],
            'macd_signal': 'bullish' if latest['macd'] > latest['macd_signal'] else 'bearish'
        }
    
    def _check_ma_trend(self, latest):
        """Check moving average alignment"""
        if pd.isna(latest['sma_200']):
            return 'insufficient_data'
        
        # Golden Cross / Death Cross
        if latest['sma_50'] > latest['sma_200'] and latest['close'] > latest['sma_50']:
            return 'bullish'
        elif latest['sma_50'] < latest['sma_200'] and latest['close'] < latest['sma_50']:
            return 'bearish'
        else:
            return 'neutral'
    
    def _check_price_trend(self):
        """Check if price is making higher lows (bullish) or lower highs (bearish)"""
        recent = self.df.tail(50)
        
        # Find local lows and highs
        lows = recent[recent['low'] == recent['low'].rolling(window=5, center=True).min()]['low']
        highs = recent[recent['high'] == recent['high'].rolling(window=5, center=True).max()]['high']
        
        if len(lows) >= 2:
            # Check if lows are rising
            if lows.iloc[-1] > lows.iloc[-2]:
                return 'bullish'
            elif lows.iloc[-1] < lows.iloc[-2]:
                return 'bearish'
        
        return 'neutral'
    
    def _check_momentum(self, latest):
        """Check momentum indicators"""
        bullish_momentum = sum([
            latest['rsi'] > 50,
            latest['macd_histogram'] > 0,
            latest['close'] > latest['sma_20']
        ])
        
        if bullish_momentum >= 2:
            return 'bullish'
        elif bullish_momentum == 1:
            return 'neutral'
        else:
            return 'bearish'
    
    def find_support_resistance(self, lookback=100):
        """
        Find key support and resistance levels
        
        Returns:
            dict with support and resistance levels
        """
        recent = self.df.tail(lookback)
        current_price = self.df.iloc[-1]['close']
        
        # Find local highs and lows
        local_highs = recent[recent['high'] == recent['high'].rolling(window=5, center=True).max()]['high']
        local_lows = recent[recent['low'] == recent['low'].rolling(window=5, center=True).min()]['low']
        
        # Cluster nearby levels
        resistance_levels = self._cluster_levels(local_highs[local_highs > current_price])
        support_levels = self._cluster_levels(local_lows[local_lows < current_price])
        
        return {
            'current_price': current_price,
            'resistance': sorted(resistance_levels)[:3],  # Top 3 resistance
            'support': sorted(support_levels, reverse=True)[:3],  # Top 3 support
            'nearest_resistance': min(resistance_levels) if resistance_levels else None,
            'nearest_support': max(support_levels) if support_levels else None
        }
    
    def _cluster_levels(self, levels, threshold=0.01):
        """Cluster nearby price levels"""
        if len(levels) == 0:
            return []
        
        levels = sorted(levels.values)
        clusters = []
        current_cluster = [levels[0]]
        
        for level in levels[1:]:
            if abs(level - np.mean(current_cluster)) / np.mean(current_cluster) < threshold:
                current_cluster.append(level)
            else:
                clusters.append(np.mean(current_cluster))
                current_cluster = [level]
        
        clusters.append(np.mean(current_cluster))
        return clusters
    
    def generate_entry_signals(self):
        """
        Generate buy/sell/short entry signals
        
        Returns:
            dict with signal information
        """
        latest = self.df.iloc[-1]
        trend = self.detect_trend()
        levels = self.find_support_resistance()
        
        # Calculate signal scores
        buy_score = 0
        sell_score = 0
        short_score = 0
        
        # Trend-based scoring
        if trend['trend'] in ['BULL MARKET', 'BULLISH']:
            buy_score += 3
        elif trend['trend'] in ['BEAR MARKET', 'BEARISH']:
            short_score += 3
        
        # RSI signals
        if latest['rsi'] < 30:  # Oversold
            buy_score += 2
        elif latest['rsi'] > 70:  # Overbought
            sell_score += 2
            if trend['trend'] in ['BEAR MARKET', 'BEARISH']:
                short_score += 2
        
        # MACD signals
        if latest['macd'] > latest['macd_signal'] and latest['macd_histogram'] > 0:
            buy_score += 2
        elif latest['macd'] < latest['macd_signal'] and latest['macd_histogram'] < 0:
            sell_score += 2
            short_score += 1
        
        # Bollinger Band signals
        if latest['bb_position'] < 0.2:  # Near lower band
            buy_score += 2
        elif latest['bb_position'] > 0.8:  # Near upper band
            sell_score += 2
            short_score += 1
        
        # Support/Resistance proximity
        current_price = latest['close']
        if levels['nearest_support']:
            distance_to_support = (current_price - levels['nearest_support']) / current_price
            if distance_to_support < 0.01:  # Within 1% of support
                buy_score += 2
        
        if levels['nearest_resistance']:
            distance_to_resistance = (levels['nearest_resistance'] - current_price) / current_price
            if distance_to_resistance < 0.01:  # Within 1% of resistance
                sell_score += 2
                short_score += 1
        
        # Volume confirmation
        if latest['volume_ratio'] > 1.5:  # High volume
            # Amplify strongest signal
            if buy_score > sell_score and buy_score > short_score:
                buy_score += 1
            elif sell_score > buy_score:
                sell_score += 1
            elif short_score > buy_score:
                short_score += 1
        
        # Determine primary signal
        max_score = max(buy_score, sell_score, short_score)
        
        if max_score < 5:
            signal = 'WAIT'
            action = 'No clear signal - wait for better setup'
            confidence = 'LOW'
        elif buy_score == max_score:
            signal = 'BUY'
            action = 'Long entry opportunity'
            confidence = 'HIGH' if buy_score >= 7 else 'MEDIUM'
        elif sell_score == max_score:
            signal = 'SELL'
            action = 'Take profit / Exit long'
            confidence = 'HIGH' if sell_score >= 7 else 'MEDIUM'
        else:
            signal = 'SHORT'
            action = 'Short entry opportunity'
            confidence = 'HIGH' if short_score >= 7 else 'MEDIUM'
        
        # Calculate entry, stop loss, and target
        entry_levels = self._calculate_entry_levels(signal, latest, levels, trend)
        
        return {
            'signal': signal,
            'action': action,
            'confidence': confidence,
            'scores': {
                'buy': buy_score,
                'sell': sell_score,
                'short': short_score
            },
            'trend_context': trend['trend'],
            'entry': entry_levels['entry'],
            'stop_loss': entry_levels['stop_loss'],
            'target': entry_levels['target'],
            'risk_reward': entry_levels['risk_reward'],
            'reasoning': self._generate_reasoning(signal, latest, trend, levels)
        }
    
    def _calculate_entry_levels(self, signal, latest, levels, trend):
        """Calculate entry, stop loss, and target levels"""
        current_price = latest['close']
        atr = latest['atr']
        
        if signal == 'BUY':
            entry = current_price
            stop_loss = levels['nearest_support'] if levels['nearest_support'] else current_price - (2 * atr)
            target = levels['nearest_resistance'] if levels['nearest_resistance'] else current_price + (3 * atr)
        
        elif signal == 'SHORT':
            entry = current_price
            stop_loss = levels['nearest_resistance'] if levels['nearest_resistance'] else current_price + (2 * atr)
            target = levels['nearest_support'] if levels['nearest_support'] else current_price - (3 * atr)
        
        elif signal == 'SELL':
            entry = current_price
            stop_loss = current_price + (1.5 * atr)
            target = current_price  # Already at target (exit signal)
        
        else:  # WAIT
            entry = levels['nearest_support'] if levels['nearest_support'] else current_price * 0.98
            stop_loss = entry * 0.97
            target = levels['nearest_resistance'] if levels['nearest_resistance'] else entry * 1.03
        
        # Calculate risk/reward
        risk = abs(entry - stop_loss)
        reward = abs(target - entry)
        risk_reward = reward / risk if risk > 0 else 0
        
        return {
            'entry': round(entry, 2),
            'stop_loss': round(stop_loss, 2),
            'target': round(target, 2),
            'risk_reward': round(risk_reward, 2)
        }
    
    def _generate_reasoning(self, signal, latest, trend, levels):
        """Generate human-readable reasoning for the signal"""
        reasons = []
        
        # Trend
        reasons.append(f"Market trend: {trend['trend']}")
        
        # RSI
        if latest['rsi'] < 30:
            reasons.append(f"RSI oversold at {latest['rsi']:.1f}")
        elif latest['rsi'] > 70:
            reasons.append(f"RSI overbought at {latest['rsi']:.1f}")
        else:
            reasons.append(f"RSI neutral at {latest['rsi']:.1f}")
        
        # MACD
        if latest['macd'] > latest['macd_signal']:
            reasons.append("MACD bullish crossover")
        else:
            reasons.append("MACD bearish crossover")
        
        # Price position
        if latest['bb_position'] < 0.3:
            reasons.append("Price near lower Bollinger Band")
        elif latest['bb_position'] > 0.7:
            reasons.append("Price near upper Bollinger Band")
        
        # Support/Resistance
        if levels['nearest_support']:
            distance = ((latest['close'] - levels['nearest_support']) / latest['close']) * 100
            reasons.append(f"Support at ${levels['nearest_support']:.2f} ({distance:.1f}% below)")
        
        if levels['nearest_resistance']:
            distance = ((levels['nearest_resistance'] - latest['close']) / latest['close']) * 100
            reasons.append(f"Resistance at ${levels['nearest_resistance']:.2f} ({distance:.1f}% above)")
        
        return reasons

def main():
    """Test the trading signals module"""
    # This would normally load real data
    print("Trading Signals Module - Ready to integrate")
    print("Use with real market data from fetch_data.py")

if __name__ == '__main__':
    main()
