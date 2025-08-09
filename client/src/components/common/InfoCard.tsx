import { Typography, Card, Backdrop, CircularProgress, CardContent, Alert, CardActions, Button } from "@mui/material";

const InfoCard = ({ title, loading, error, refetch, children }) => {
    return (
        <Card
            sx={{
                position: 'relative',
                borderRadius: 2,
                boxShadow: 3,
                opacity: loading ? 0.5 : 1,
                transition: 'opacity 0.3s ease',
                height: '45vh',
                width: '20vw'
            }}
        >
            {/* Loading Backdrop */}
            <Backdrop
                sx={{
                    position: 'absolute',
                    color: '#fff',
                    zIndex: (theme) => theme.zIndex.drawer + 1,
                }}
                open={loading}
            >
                <CircularProgress color="inherit" />
            </Backdrop>

            <CardContent>
                <Typography variant="h5" gutterBottom>
                    {title}
                </Typography>
                {error && (
                    <Alert
                        severity="error"
                        action={
                            <Button color="inherit" size="small" onClick={refetch} sx={{ textTransform: 'none' }}>
                                Refetch
                            </Button>
                        }
                    >
                        {error}
                    </Alert>
                )}
                <Typography variant="body2">
                    {children}
                </Typography>
            </CardContent>

            {/* <CardActions>
        <Button
          size="small"
          disabled={loading}
          onClick={onAction}
        >
          Action
        </Button>
      </CardActions> */}
        </Card>
    )
};

export default InfoCard;