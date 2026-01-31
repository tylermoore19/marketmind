import { useApiCall } from '../hooks/useApiCall';
import api from '../services/api';
import InfoCard from '../components/common/InfoCard';
import { useTheme } from '@mui/material/styles';
import FlexWrapLayout from '../layouts/FlexWrapLayout';
import GridLayoutTesting from '../layouts/GridLayout';

const StocksPage = () => {
    const bullishStocksCard = useApiCall(api.getBullishStocks);
    // const bearishStocksCard = useApiCall(api.getBearishStocks);

    const theme = useTheme();

    const bullishData = Array.isArray(bullishStocksCard.data)
        ? bullishStocksCard.data.map((it: any) => ({
            ...it,
            _rightColor: (it?.buy_signal === 'Buy') ? theme.palette.success.main : theme.palette.error.main
        }))
        : null;

    // const bearishData = Array.isArray(bearishStocksCard.data)
    //     ? bearishStocksCard.data.map((it: any) => ({
    //         ...it,
    //         _rightColor: (it?.buy_signal === 'Sell') ? theme.palette.success.main : theme.palette.error.main
    //     }))
    //     : null;

    return (
        <FlexWrapLayout>
            <InfoCard
                title="Bullish Stocks"
                loading={bullishStocksCard.loading}
                error={bullishStocksCard.error}
                refetch={bullishStocksCard.fetch}
                data={bullishData}
                dataHeaderKey={'ticker'}
                dataRightKey={'buy_signal'}
            />
            {/* 
            <InfoCard
                title="Bearish Stocks"
                loading={bearishStocksCard.loading}
                error={bearishStocksCard.error}
                refetch={bearishStocksCard.fetch}
                data={bearishData}
                dataHeaderKey={'ticker'}
                dataRightKey={'buy_signal'}
            /> */}
        </FlexWrapLayout>
        // <GridLayoutTesting />
    )
};

export default StocksPage;