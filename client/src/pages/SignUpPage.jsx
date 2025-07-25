import AuthLayout from '../layouts/AuthLayout';
import SignUpForm from '../auth/SignUpForm';

const SignUpPage = () => {
    const handleSignUp = (credentials) => {
        // TODO: Implement sign up logic (API call, context, etc.)
        console.log('Sign up submitted:', credentials);
    };

    return (
        <AuthLayout>
            <SignUpForm onSubmit={handleSignUp} />
        </AuthLayout>
    );
};

export default SignUpPage;
