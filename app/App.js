import React, { useCallback, useEffect, useRef, useState } from 'react';
import { ActivityIndicator, AppState, BackHandler, Platform, SafeAreaView, Settings, StyleSheet, Text, View } from 'react-native';
import { WebView } from 'react-native-webview';
import { Asset } from 'expo-asset';
import * as Haptics from 'expo-haptics';
import * as FileSystem from 'expo-file-system';
import { useKeepAwake } from 'expo-keep-awake';
import { Share } from 'react-native';
import * as SplashScreen from 'expo-splash-screen';
import { StatusBar } from 'expo-status-bar';
import * as GameServices from 'react-native-game-services';
import * as Updates from 'expo-updates';
import { setAudioModeAsync } from 'expo-audio';

SplashScreen.preventAutoHideAsync().catch(() => {});

const GAME = require('./assets/game/index.html');

/* The meta profile (permanent upgrades) is the only state that must survive
   the app being closed. The page persists it to localStorage, but a
   file:// origin is not somewhere to trust a player's progression, so the
   native side keeps the authoritative copy in a real file and hands it to
   the page before load. */
const META_FILE = FileSystem.documentDirectory + 'altay-meta.json';

/* OTA. expo-updates' default is to download in the background and apply on the
   NEXT launch, which would mean telling a player to close and reopen twice
   before co-op stops reporting a version mismatch. Instead this checks while
   the splash is already up for the art bake, and if an update is genuinely
   waiting it fetches and reloads there and then -- one restart, as the
   in-game message promises. A missing or slow update server must never hold
   the game hostage, so the whole thing is bounded and every failure path just
   plays the build already installed. */
const UPDATE_CHECK_MS = 3000;
const UPDATE_FETCH_MS = 12000;
const withTimeout = (promise, ms) =>
  Promise.race([promise, new Promise((res) => setTimeout(() => res('__timeout'), ms))]);

async function applyPendingUpdate(onDownloading) {
  if (__DEV__ || !Updates.isEnabled) return false;
  try {
    const check = await withTimeout(Updates.checkForUpdateAsync(), UPDATE_CHECK_MS);
    if (check === '__timeout' || !check || !check.isAvailable) return false;
    // an update really is being fetched: tell the player, instead of leaving
    // them on a dark splash that looks like a hang
    if (onDownloading) onDownloading();
    const fetched = await withTimeout(Updates.fetchUpdateAsync(), UPDATE_FETCH_MS);
    if (fetched === '__timeout' || !fetched || !fetched.isNew) return false;
    await Updates.reloadAsync();   // does not return: the app restarts here
    return true;
  } catch (e) {
    return false;                  // offline, no server configured, anything
  }
}

/* Game Center leaderboards, one per difficulty so a hard-mode run is not
   ranked against an easy one. These IDs must match what is created in App
   Store Connect exactly -- submitting to an ID that does not exist there
   fails silently, which is the usual reason a leaderboard "does not work".
   Ranked by score (the run's bounty total) rather than waves survived:
   plenty of players will finish all 32 waves, and score breaks those ties. */
const LEADERBOARDS = {
  easy: 'altay.score.easy',
  normal: 'altay.score.normal',
  hard: 'altay.score.hard'
};

async function readMeta() {
  try {
    const info = await FileSystem.getInfoAsync(META_FILE);
    if (!info.exists) return null;
    const raw = await FileSystem.readAsStringAsync(META_FILE);
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === 'object' ? parsed : null;
  } catch (e) { return null; }
}

async function writeMeta(meta) {
  try { await FileSystem.writeAsStringAsync(META_FILE, JSON.stringify(meta)); } catch (e) { }
}

/* Injected before the page's own scripts run.
   Two jobs:
   1. Give the page a native handle it can feature-detect, so the same file
      keeps working unmodified in a browser (where the handle is simply absent).
   2. Kill the gestures a full-screen canvas game must not have -- pinch-zoom,
      double-tap zoom, long-press callouts, text selection and rubber-band
      scrolling all fight the game's own pan/zoom handling. */
/* The phone's language, handed to the page as __altayLocale. Inside the
   WebView navigator.language follows the app bundle's localizations, not the
   device, so the page cannot find out on its own. AppleLanguages is the
   user's ordered preference list on iOS; Intl covers everything else. */
function deviceLocale() {
  try {
    if (Platform.OS === 'ios') {
      const langs = Settings.get('AppleLanguages');
      if (Array.isArray(langs) && langs[0]) return String(langs[0]);
      const loc = Settings.get('AppleLocale');
      if (loc) return String(loc);
    }
  } catch (e) { }
  try { return Intl.DateTimeFormat().resolvedOptions().locale || ''; } catch (e) { return ''; }
}

const injectFor = (meta) => `
  window.__altayMeta = ${meta ? JSON.stringify(meta) : 'null'};
  window.__altayLocale = ${JSON.stringify(deviceLocale())};
` + INJECT;

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
  const [meta, setMeta] = useState(undefined);   // undefined = not read yet
  const [updating, setUpdating] = useState(false);
  const webRef = useRef(null);
  useKeepAwake();   // a tower-defence wave can run minutes without a touch
  const gcReady = useRef(false);

  /* The native audio session, set once at launch -- the same configuration the
     Polderland shell uses. Without it iOS gives the WebView its default
     session (the ringer switch silences WebAudio, and a phone call, a
     notification or an app switch ends the session so the page's music never
     comes back, however often the page resumes its context). Playing in
     'playback' mode through the silent switch and mixing with other audio
     lets the system hand the session back when the app returns. */
  useEffect(() => {
    setAudioModeAsync({
      playsInSilentMode: true,
      interruptionMode: 'mixWithOthers',
      shouldPlayInBackground: false,
      allowsRecording: false,
      shouldRouteThroughEarpiece: false,
    }).catch(() => {
      // an audio session that will not configure is a quieter game, not a broken one
    });
  }, []);

  /* Authenticate against Game Center once, quietly. A player who is not
     signed in, or who declines, simply gets no leaderboard -- it must never
     block or interrupt getting into the game. */
  useEffect(() => {
    (async () => {
      try {
        GameServices.initialize();
        await GameServices.signIn();
        gcReady.current = await GameServices.isAuthenticated();
      } catch (e) { gcReady.current = false; }
    })();
  }, []);

  useEffect(() => {
    let alive = true;
    (async () => {
      // downloadAsync resolves the bundled asset to a real on-device file://
      // path; without it localUri is null on a production build.
      const asset = Asset.fromModule(GAME);
      // Run the update check alongside the asset load rather than before it,
      // so on the common path (no update) it costs nothing the splash was not
      // already spending.
      const [, , stored] = await Promise.all([
        applyPendingUpdate(() => {
          if (!alive) return;
          setUpdating(true);
          SplashScreen.hideAsync().catch(() => {});
        }), asset.downloadAsync(), readMeta()
      ]);
      if (!alive) return;
      setMeta(stored);
      setUri(asset.localUri || asset.uri);
    })();
    return () => { alive = false; };
  }, []);

  /* Coming back from the background: iOS interrupts the WebView's audio and
     the page cannot always tell. Say so explicitly so it can resume the music. */
  useEffect(() => {
    const sub = AppState.addEventListener('change', (st) => {
      if (st === 'active') webRef.current?.injectJavaScript('window.dispatchEvent(new Event("altay:resume"));true;');
      else webRef.current?.injectJavaScript('window.dispatchEvent(new Event("altay:background"));true;');
    });
    return () => sub.remove();
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
      case 'meta':
        writeMeta(msg.payload);
        break;
      case 'score': {
        /* Submitted silently. Throwing a share sheet in the player's face the
           instant a run ends is an interruption they did not ask for; the end
           screen has a button for the leaderboard and one for sharing. */
        const p = msg.payload || {};
        const board = LEADERBOARDS[p.difficulty] || LEADERBOARDS.normal;
        if (gcReady.current) {
          GameServices.submitScore(board, Math.max(0, p.score | 0)).catch(() => {});
        }
        break;
      }
      case 'leaderboard': {
        const p = msg.payload || {};
        const board = LEADERBOARDS[p.difficulty] || LEADERBOARDS.normal;
        if (gcReady.current) GameServices.showLeaderboard(board).catch(() => {});
        break;
      }
      case 'share': {
        const p = msg.payload || {};
        const line = p.lang === 'tr'
          ? (p.won
            ? `Altay'da ${p.wave} dalganın hepsini tuttum. Puan ${p.score}.`
            : `Altay'da ${p.wave}. dalgada düştüm. Puan ${p.score}.`)
          : (p.won
            ? `I held all ${p.wave} waves in Altay. Score ${p.score}.`
            : `I fell on wave ${p.wave} in Altay. Score ${p.score}.`);
        Share.share({ message: line }).catch(() => {});
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

  if (!uri || meta === undefined) {
    if (!updating) return <View style={styles.root} />;
    const tr = /^tr/i.test(deviceLocale());
    return (
      <View style={[styles.root, styles.center]}>
        <StatusBar hidden />
        <Text style={styles.title}>ALTAY</Text>
        <ActivityIndicator size="small" color="#d6ac5c" style={{ marginTop: 18 }} />
        <Text style={styles.sub}>{tr ? 'Güncelleniyor…' : 'Updating…'}</Text>
      </View>
    );
  }

  /* SafeAreaView, not env(safe-area-inset-*) in the page alone: inside the
     WebView env() came back 0 on a real iPhone, so the HUD's top bar slid
     under the Dynamic Island. This pads the WebView by the native insets
     (island / rounded corners / home indicator, portrait or landscape), and
     the page's own env() handling stays as a harmless second layer for
     browsers. The padding shows the same obsidian as the page behind it. */
  return (
    <SafeAreaView style={styles.root}>
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
        injectedJavaScriptBeforeContentLoaded={injectFor(meta)}
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
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: '#0b0d12' },
  web: { flex: 1, backgroundColor: '#0b0d12' },
  center: { alignItems: 'center', justifyContent: 'center' },
  title: { color: '#e8c27a', fontSize: 34, fontWeight: '900', letterSpacing: 6 },
  sub: { color: '#8b8676', fontSize: 13, letterSpacing: 1, marginTop: 10 },
});
