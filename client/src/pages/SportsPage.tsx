import { useApiCall } from '../hooks/useApiCall';
import api from '../services/api';
import InfoCard from '../components/common/InfoCard';
import FlexWrapLayout from '../layouts/FlexWrapLayout';
import GridLayoutTesting from '../layouts/GridLayout';

const SportsPage = () => {
    // const sportsPredictionCard = useApiCall(api.getSportsPredictions);
    const sportsParlayCard = useApiCall(api.getSportsParlay);

    return (
        <FlexWrapLayout>
            {/* <InfoCard
                title="Sports Predictions"
                loading={sportsPredictionCard.loading}
                error={sportsPredictionCard.error}
                refetch={sportsPredictionCard.fetch}
                data={sportsPredictionCard.data}
                dataHeaderKey={'bet'}
                dataRightKey={'unitSize'}
            /> */}
            <InfoCard
                title="Sports Parlay"
                loading={sportsParlayCard.loading}
                error={sportsParlayCard.error}
                refetch={sportsParlayCard.fetch}
                data={(sportsParlayCard.data as { parlay?: { legs?: any[] } })?.parlay?.legs ?? []}
                dataHeaderKey={'bet'}
                dataRightKey={'estimatedProbability'}
            />
        </FlexWrapLayout>
        // <GridLayoutTesting />
    )
};

export default SportsPage;