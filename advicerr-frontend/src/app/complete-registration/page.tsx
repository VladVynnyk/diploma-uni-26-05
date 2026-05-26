import React, { Suspense } from 'react';
import CompleteRegistrationWContainer from './CompleteRegistrationWContainer';
import { completeRegistrationMetadata } from './metadata';

export const metadata = completeRegistrationMetadata;

const CompleteRegistrationPage = () => {
  return (
    <Suspense fallback={null}>
      <CompleteRegistrationWContainer />
    </Suspense>
  );
};

export default CompleteRegistrationPage;
