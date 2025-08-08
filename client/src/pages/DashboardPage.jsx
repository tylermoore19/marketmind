import { useApiCall } from '../hooks/useApiCall';
import api from '../services/api';

const DashboardPage = () => {
    const callRoot = useApiCall(api.getRoot);

    const handleCallBackend = async () => {
        const data = await callRoot();

        console.log('Backend response:', data);
    };

    return (
        <div style={{ minHeight: '80vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <h1>Dashboard</h1>
            <button
                style={{ marginTop: 24, padding: '8px 20px', fontSize: 16, borderRadius: 6, border: '1px solid #1976d2', background: '#1976d2', color: '#fff', cursor: 'pointer' }}
                onClick={handleCallBackend}
            >
                Call Backend Home
            </button>
        </div>
    );
};

export default DashboardPage;
