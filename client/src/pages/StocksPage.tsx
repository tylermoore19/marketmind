import { useApiCall } from '../hooks/useApiCall';
import api from '../services/api';
import InfoCard from '../components/common/InfoCard';
import { useTheme } from '@mui/material/styles';
import FlexWrapLayout from '../layouts/FlexWrapLayout';
import GridLayoutTesting from '../layouts/GridLayout';

const StocksPage = () => {
    const topStocksCard = useApiCall(api.getTopStocks);
    const bullishStocksCard = useApiCall(api.getBullishStocks);

    const theme = useTheme();

    const bullishData = Array.isArray(bullishStocksCard.data)
        ? bullishStocksCard.data.map((it: any) => ({
            ...it,
            _rightColor: (it?.buy_signal === 'Buy') ? theme.palette.success.main : theme.palette.error.main
        }))
        : null;

    return (
        <FlexWrapLayout>
            {/* <InfoCard title="Top Stocks" loading={topStocksCard.loading} error={topStocksCard.error} refetch={topStocksCard.fetch}>
                {topStocksCard.data ? <pre>{JSON.stringify(topStocksCard.data, null, 2)}</pre> : null}
            </InfoCard> */}

            <InfoCard
                title="Bullish Stocks"
                loading={bullishStocksCard.loading}
                error={bullishStocksCard.error}
                refetch={bullishStocksCard.fetch}
                data={bullishData}
                dataHeaderKey={'ticker'}
                dataRightKey={'buy_signal'}
            />
        </FlexWrapLayout>
        // <GridLayoutTesting />
    )
};

export default StocksPage;