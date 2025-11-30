import { Typography, Card, Backdrop, CircularProgress, CardContent, Alert, CardActions, Button, Collapse, List, ListItem, Box } from "@mui/material";
import { useState, type FC, type ReactNode } from 'react';

interface InfoCardProps {
    title: ReactNode;
    loading?: boolean;
    error?: ReactNode;
    refetch?: () => void;
    // optional structured data display
    data?: any[] | null | unknown;
    dataHeaderKey?: string; // property name to show on left as header
    dataRightKey?: string; // property name to show on right side
}

const InfoCard: FC<InfoCardProps> = ({ title, loading = false, error, refetch, data = null, dataHeaderKey, dataRightKey }) => {

    const JsonListItem = ({ item, idx }: { item: any; idx: number }) => {
        const [open, setOpen] = useState(false);
        const left = dataHeaderKey ? (item?.[dataHeaderKey] ?? String(idx)) : String(idx);
        const right = dataRightKey ? (item?.[dataRightKey] ?? String(idx)) : String(idx);
        const rightColor = item?._rightColor ?? 'text.secondary';
        return (
            <Box sx={{ width: '100%', border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                <Button fullWidth onClick={() => setOpen(v => !v)} sx={{ justifyContent: 'space-between', textTransform: 'none' }}>
                    <Box sx={{ textAlign: 'left', overflow: 'hidden', textOverflow: 'ellipsis' }}>{left}</Box>
                    <Box sx={{ bgcolor: rightColor, ml: 2, whiteSpace: 'nowrap', px: 1, py: 0.25, borderRadius: 0.5, color: 'text.primary' }}>{right}</Box>
                </Button>
                <Collapse in={open} timeout="auto" unmountOnExit>
                    <Box sx={{ p: 1, fontFamily: 'monospace', fontSize: 12, bgcolor: 'background.paper', borderRadius: 1 }}>
                        <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{JSON.stringify(item, null, 2)}</pre>
                    </Box>
                </Collapse>
            </Box>
        );
    };

    return (
        <Card
            sx={{
                position: 'relative',
                display: 'flex',
                flexDirection: 'column',
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

            <CardContent sx={{ display: 'flex', flexDirection: 'column', minHeight: 0 }}>
                <Typography variant="h6" color="primary" align="left" gutterBottom>
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

                {/* scrollable list area */}
                <Box sx={{ overflowY: 'auto' }}>
                    {Array.isArray(data) ? (
                        data.map((it, i) => (
                            <ListItem key={i} disableGutters sx={{ py: 0.5 }}>
                                <JsonListItem item={it} idx={i} />
                            </ListItem>
                        ))
                    ) : null}
                </Box>
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