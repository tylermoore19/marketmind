import '@mui/material/styles';

declare module '@mui/material/styles' {
    interface Palette {
        gradients?: {
            orange: string;
            // add other gradient properties you use
        };
    }

    interface PaletteOptions {
        gradients?: {
            orange?: string;
            // add other gradient properties you use
        };
    }

    interface Theme {
        appSpecific: {
            padding: {
                lg: number;
                xlg: number;
            };
        };
    }
    interface ThemeOptions {
        appSpecific?: {
            padding?: {
                lg?: number;
                xlg?: number;
            };
        };
    }
}
