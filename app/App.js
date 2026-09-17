import React, { useCallback, useEffect, useRef, useState } from 'react';
import { BackHandler, Platform, StyleSheet, View } from 'react-native';
import { WebView } from 'react-native-webview';
import { Asset } from 'expo-asset';
import * as Haptics from 'expo-haptics';
import * as SplashScreen from 'expo-splash-screen';
import { StatusBar } from 'expo-status-bar';

SplashScreen.preventAutoHideAsync().catch(() => {});

const GAME = require('./assets/game/index.html');

/* Injected before the page's own scripts run.
   Two jobs:
   1. Give the page a native handle it can feature-detect, so the same file
      keeps working unmodified in a browser (where the handle is simply absent).
   2. Kill the gestures a full-screen canvas game must not have -- pinch-zoom,
      double-tap zoom, long-press callouts, text selection and rubber-band
      scrolling all fight the game's own pan/zoom handling. */
const INJECT = `
(function () {
  if (window.__altayNative) return;
  var rn = window.ReactNativeWebView;
  window.__altayNative = {
    version: 1,
    post: function (type, payload) {
      try { rn && rn.postMessage(JSON.stringify({ type: type, payload: payload })); } catch (e) {}
    }
  };
  var css = document.createElement('style');
  css.textContent =
    '*{-webkit-touch-callout:none;-webkit-user-select:none;user-select:none;}' +
    'html,body{overscroll-behavior:none;touch-action:none;position:fixed;' +
    'width:100%;height:100%;overflow:hidden;margin:0;}';
  (document.head || document.documentElement).appendChild(css);
  document.addEventListener('gesturestart', function (e) { e.preventDefault(); }, { passive: false });
  document.addEventListener('contextmenu', function (e) { e.preventDefault(); });
  var lastTouch = 0;
  document.addEventListener('touchend', function (e) {
    var now = Date.now();
    if (now - lastTouch < 320) e.preventDefault();   // double-tap zoom
    lastTouch = now;
  }, { passive: false });
})();
true;
`;

export default function App() {
  const [uri, setUri] = useState(null);
  const webRef = useRef(null);

  useEffect(() => {
    let alive = true;
    (async () => {
      // downloadAsync resolves the bundled asset to a real on-device file://
      // path; without it localUri is null on a production build.
      const asset = Asset.fromModule(GAME);
      await asset.downloadAsync();
      if (alive) setUri(asset.localUri || asset.uri);
    })();
    return () => { alive = false; };
  }, []);

  // Android's hardware back button would otherwise leave the game; keep it
  // inside the app and let the page decide what "back" means.
  useEffect(() => {
    if (Platform.OS !== 'android') return;
    const sub = BackHandler.addEventListener('hardwareBackPress', () => {
      webRef.current?.injectJavaScript('window.dispatchEvent(new Event("altay:back"));true;');
      return true;
    });
    return () => sub.remove();
  }, []);

  const onMessage = useCallback((event) => {
    let msg;
    try { msg = JSON.parse(event.nativeEvent.data); } catch (e) { return; }
    switch (msg && msg.type) {
      case 'haptic': {
        const k = msg.payload;
        if (k === 'heavy') Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
        else if (k === 'medium') Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
        else if (k === 'success') Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        else if (k === 'warning') Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
        else if (k === 'error') Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
        else Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
        break;
      }
      default:
        break;
    }
  }, []);

  const onLoadEnd = useCallback(() => {
    // The page bakes its art before it is usable, so hold the splash until the
    // game says it is ready rather than until the WebView reports a load.
    SplashScreen.hideAsync().catch(() => {});
  }, []);

  if (!uri) return <View style={styles.root} />;

  return (
    <View style={styles.root}>
      <StatusBar hidden />
      <WebView
        ref={webRef}
        source={{ uri }}
        style={styles.web}
        // a file:// page needs read access to its own directory for the
        // bundled asset, and an origin it can keep localStorage against
        originWhitelist={['*']}
        allowFileAccess
        allowFileAccessFromFileURLs
        allowUniversalAccessFromFileURLs
        injectedJavaScriptBeforeContentLoaded={INJECT}
        onMessage={onMessage}
        onLoadEnd={onLoadEnd}
        // canvas-game ergonomics
        scrollEnabled={false}
        bounces={false}
        overScrollMode="never"
        showsHorizontalScrollIndicator={false}
        showsVerticalScrollIndicator={false}
        setSupportMultipleWindows={false}
        mediaPlaybackRequiresUserAction={false}
        allowsInlineMediaPlayback
        textZoom={100}
        // WebRTC for co-op needs the page to be treated as a normal origin
        javaScriptEnabled
        domStorageEnabled
        cacheEnabled={false}
        androidLayerType="hardware"
      />
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: '#0b0d12' },
  web: { flex: 1, backgroundColor: '#0b0d12' },
});
