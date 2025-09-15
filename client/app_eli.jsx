// App.jsx
import React, { useState, useEffect } from 'react';
import {Line} from 'react-chartjs-2';
import './styles.css';

function App() {
  const [agentData, setAgentData] = useState({
    AgriVision: null,
    SoilSense: null, 
    CropMaster: null
  });
  
  const [isConnected, setIsConnected] = useState(false);
  const [currentScenario, setCurrentScenario] = useState(null);
  const [status, setStatus] = useState('Conectando...');
  const [wsRef, setWsRef] = useState(null);

  useEffect(() => {
    let ws = null;
    let reconnectTimer = null;

    const connectWebSocket = () => {
      try {
        ws = new WebSocket('ws://localhost:8000/ws');
        setWsRef(ws);

        ws.onopen = (event) => {
          console.log('✅ WebSocket conectado exitosamente:', event);
          setIsConnected(true);
          setStatus('Conectado - Esperando datos...');
          
          // Limpiar timer de reconexión si existe
          if (reconnectTimer) {
            clearTimeout(reconnectTimer);
            reconnectTimer = null;
          }
        };

        ws.onmessage = (event) => {
          try {
            console.log('📨 Mensaje recibido:', event.data);
            const message = JSON.parse(event.data);
            
            // Manejar diferentes tipos de mensajes
            switch (message.type) {
              case 'agent_result':
                console.log(`🤖 Resultado de ${message.agent}:`, message.data);
                setAgentData(prev => ({
                  ...prev,
                  [message.agent]: message.data
                }));
                break;
                
              case 'scenario':
                console.log('🎯 Nuevo escenario:', message.data);
                setCurrentScenario(message.data);
                setStatus(`Analizando: ${message.data.name}`);
                break;
                
              case 'status':
                console.log('📊 Estado:', message.message);
                setStatus(message.message);
                break;
                
              case 'error':
                console.error('❌ Error del servidor:', message.message);
                setStatus(`Error: ${message.message}`);
                break;
                
              default:
                console.log('📋 Mensaje no categorizado:', message);
            }
            
            // NO cerrar la conexión aquí - esto era el problema principal
          } catch (error) {
            console.error('❌ Error parsing JSON:', error, 'Data:', event.data);
            // NO cerrar la conexión por errores de parsing
          }
        };

        ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
          setStatus('Error de conexión');
          // NO cerrar la conexión aquí
        };

        ws.onclose = (event) => {
          console.log('🔌 WebSocket cerrado:', event.code, event.reason);
          setIsConnected(false);
          setStatus('Desconectado');
          
          // Solo reconectar si no fue una desconexión intencional
          if (event.code !== 1000) { // 1000 = cierre normal
            console.log('🔄 Intentando reconectar en 3 segundos...');
            setStatus('Reconectando...');
            reconnectTimer = setTimeout(() => {
              connectWebSocket();
            }, 3000);
          }
        };

      } catch (error) {
        console.error('❌ Error creando WebSocket:', error);
        setStatus('Error al conectar');
      }
    };

    // Iniciar conexión
    connectWebSocket();

    // Cleanup function mejorado
    return () => {
      console.log('🧹 Limpiando conexión WebSocket...');
      if (reconnectTimer) {
        clearTimeout(reconnectTimer);
      }
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close(1000, 'Componente desmontado'); // Cierre limpio
      }
    };
  }, []);

  return (
    <div className="min-h-screen bg-green-50 p-8">
      {/* Header con indicador de estado */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-green-800 mb-4">
          🌱 AgroTech AI Agents Demo
        </h1>
        
        {/* Indicador de estado de conexión */}
        <div className="flex justify-center items-center space-x-4 mb-4">
          <div className={`flex items-center space-x-2 px-4 py-2 rounded-full ${
            isConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            <div className={`w-3 h-3 rounded-full ${
              isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
            }`}></div>
            <span className="font-medium">
              {isConnected ? '🟢 Conectado' : '🔴 Desconectado'}
            </span>
          </div>
          
          {/* Estado actual */}
          <div className="bg-blue-100 text-blue-800 px-4 py-2 rounded-full">
            <span className="font-medium">{status}</span>
          </div>
        </div>
        
        {/* Escenario actual */}
        {currentScenario && (
          <div className="bg-yellow-100 text-yellow-800 px-6 py-3 rounded-lg inline-block">
            <span className="font-semibold">{currentScenario.name}</span>
            {currentScenario.description && (
              <div className="text-sm mt-1">{currentScenario.description}</div>
            )}
          </div>
        )}
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Agente AgriVision */}
        <AgentCard 
          title="🔍 AgriVision" 
          data={agentData.AgriVision}
          color="blue"
        />
        
        {/* Agente SoilSense */}
        <AgentCard 
          title="🌍 SoilSense" 
          data={agentData.SoilSense}
          color="brown"
        />
        
        {/* Agente CropMaster */}
        <AgentCard 
          title="🧠 CropMaster" 
          data={agentData.CropMaster}
          color="green"
        />
      </div>
      
      {/* Panel de Decisión Final */}
      <DecisionPanel data={agentData.CropMaster} />
      
      {/* Debug panel (opcional - puedes quitarlo en producción) */}
      {!isConnected && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mt-6">
          <h3 className="text-red-800 font-semibold mb-2">🔧 Solución de problemas:</h3>
          <ul className="text-red-700 text-sm space-y-1">
            <li>• Verifica que el servidor backend esté corriendo en puerto 8000</li>
            <li>• Ejecuta: <code>python main.py</code> en la carpeta server</li>
            <li>• Prueba la conexión en: <a href="http://localhost:8000/ws/test" className="underline">http://localhost:8000/ws/test</a></li>
          </ul>
        </div>
      )}
    </div>
  );
}

function AgentCard({ title, data, color }) {
  return (
    <div className={`bg-white rounded-lg shadow-lg p-6 border-l-4 border-${color}-500`}>
      <h3 className="text-xl font-semibold mb-4">{title}</h3>
      {data ? (
        <div className="space-y-2">
          {Object.entries(data).map(([key, value]) => (
            <div key={key} className="flex justify-between">
              <span className="text-gray-600">{key}:</span>
              <span className="font-medium">
                {typeof value === 'object' ? JSON.stringify(value) : String(value)}
              </span>
            </div>
          ))}
        </div>
      ) : (
        <div className="animate-pulse">Analizando...</div>
      )}
    </div>
  );
}

function DecisionPanel({ data }) {
  if (!data) return null;
  
  const statusColors = {
    excellent: 'bg-green-100 text-green-800',
    good: 'bg-blue-100 text-blue-800', 
    warning: 'bg-yellow-100 text-yellow-800',
    critical: 'bg-red-100 text-red-800'
  };
  
  return (
    <div className="bg-white rounded-lg shadow-lg p-8">
      <h2 className="text-2xl font-bold mb-6 text-center">📊 Decisión Final del Sistema</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-lg font-semibold mb-3">Estado General</h3>
          <span className={`px-4 py-2 rounded-full ${statusColors[data.overall_status]}`}>
            {data.overall_status?.toUpperCase()}
          </span>
        </div>
        
        <div>
          <h3 className="text-lg font-semibold mb-3">Acciones Prioritarias</h3>
          <ul className="list-disc list-inside space-y-1">
            {data.priority_actions?.map((action, index) => (
              <li key={index} className="text-gray-700">{action}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

export default App;