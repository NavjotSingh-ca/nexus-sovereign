@echo off
echo Setting up GitHub secrets for Nexus Sovereign...
echo.

echo IMPORTANT: You need to create these secrets in your GitHub repository settings:
echo.
echo 1. Go to your GitHub repository
echo 2. Click Settings -> Secrets and variables -> Actions
echo 3. Click "New repository secret"
echo.
echo Add these secrets:
echo.

echo Secret: SUPABASE_URL
echo Value: %SUPABASE_URL%
echo.

echo Secret: SUPABASE_KEY  
echo Value: %SUPABASE_KEY%
echo.

echo Your current values are:
echo SUPABASE_URL=%SUPABASE_URL%
echo SUPABASE_KEY=%SUPABASE_KEY%
echo.

echo After adding secrets, the GitHub Action will run every 15 minutes automatically.
echo The system will be immortal - running 24/7 in the cloud!
echo.

pause