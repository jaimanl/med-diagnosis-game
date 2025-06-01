import React, { useState } from 'react';
import PlayerForm from './PlayerForm';
import Game from './Game';
import AdminDashboard from './AdminDashboard';

function App() {
  const [session, setSession] = useState(null);
  const [adminMode, setAdminMode] = useState(false);

  return (
    <div>
      <h1>🩺 Medical Diagnosis Game</h1>
      {!session && !adminMode && (
        <>
          <button onClick={() => setAdminMode(true)}>Admin Dashboard</button>
          <PlayerForm onJoin={setSession} />
        </>
      )}
      {session && <Game session={session} />}
      {adminMode && <AdminDashboard />}
    </div>
  );
}

export default App;
