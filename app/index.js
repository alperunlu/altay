/* Entry point. This file exists specifically so registerRootComponent runs:
   pointing package.json's "main" straight at App.js means nothing ever
   registers a root component, native asks for the app named "main", finds
   nothing, and the process aborts a few hundred milliseconds after launch --
   with a crash log that shows only React Native's error reporting and sends
   you hunting in entirely the wrong place. */
import { registerRootComponent } from 'expo';
import App from './App';

registerRootComponent(App);
