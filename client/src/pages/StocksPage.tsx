import { useApiCall } from '../hooks/useApiCall';
import api from '../services/api';
import InfoCard from '../components/common/InfoCard';
import FlexWrapLayout from '../layouts/FlexWrapLayout';

const StocksPage = () => {
    const topStocksCard = useApiCall(api.getTopStocks);
    const testingStocksCard = useApiCall(api.getTestingStocks);

    return (
        <FlexWrapLayout>
            <InfoCard title="Top Stocks" loading={topStocksCard.loading} error={topStocksCard.error} refetch={topStocksCard.fetch}>
                {topStocksCard.data && <pre>{JSON.stringify(topStocksCard.data, null, 2)}</pre>}
            </InfoCard>

            <InfoCard title="Testing Stocks" loading={testingStocksCard.loading} error={testingStocksCard.error} refetch={testingStocksCard.fetch}>
                {testingStocksCard.data && <pre>{JSON.stringify(testingStocksCard.data, null, 2)}</pre>}
            </InfoCard>
        </FlexWrapLayout>
    )
};

export default StocksPage;