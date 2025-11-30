import { useApiCall } from '../hooks/useApiCall';
import api from '../services/api';
import InfoCard from '../components/common/InfoCard';
import FlexWrapLayout from '../layouts/FlexWrapLayout';
import GridLayoutTesting from '../layouts/GridLayout';

const SportsPage = () => {
    const sportsPredictionCard = useApiCall(api.getSportsPredictions);

    return (
        <FlexWrapLayout>
            {/* <InfoCard title="Sports Predictions" loading={sportsPredictionCard.loading} error={sportsPredictionCard.error} refetch={sportsPredictionCard.fetch}>
                {sportsPredictionCard.data ? <pre>{JSON.stringify(sportsPredictionCard.data, null, 2)}</pre> : null}
            </InfoCard> */}

            <InfoCard
                title="Sports Predictions"
                loading={sportsPredictionCard.loading}
                error={sportsPredictionCard.error}
                refetch={sportsPredictionCard.fetch}
                data={sportsPredictionCard.data}
                dataHeaderKey={'bet'}
                dataRightKey={'unitSize'}
            />
        </FlexWrapLayout>
        // <GridLayoutTesting />
    )
};

export default SportsPage;