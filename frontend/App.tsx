import { useState } from 'react';
import { MenuScreen } from './src/screens/MenuScreen';
import { LocationScreen } from './src/screens/LocationScreen';
import { CameraScreen } from './src/screens/CameraScreen';
import type { CaptureContext } from './src/types/inspection';

type Screen = 'menu' | 'location' | 'camera';

export default function App() {
  const [screen, setScreen] = useState<Screen>('menu');
  const [context, setContext] = useState<CaptureContext>({});

  if (screen === 'menu') {
    return <MenuScreen onStart={() => setScreen('location')} />;
  }

  if (screen === 'location') {
    return (
      <LocationScreen
        onBack={() => setScreen('menu')}
        onConfirm={(ctx) => {
          setContext(ctx);
          setScreen('camera');
        }}
      />
    );
  }

  return <CameraScreen context={context} onBack={() => setScreen('location')} />;
}