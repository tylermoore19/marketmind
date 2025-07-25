import AuthLayout from '../layouts/AuthLayout';
import LoginForm from '../auth/LoginForm';

const LoginPage = () => {
    const handleLogin = (credentials) => {
        // TODO: Implement login logic (API call, context, etc.)
        console.log('Login submitted:', credentials);
    };

    return (
        <AuthLayout>
            <LoginForm onSubmit={handleLogin} />
        </AuthLayout>
    );
};

export default LoginPage;
