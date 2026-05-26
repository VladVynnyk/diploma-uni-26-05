import React from 'react'
import Link from 'next/link';
// import { useRouter } from 'next/navigation';
import { usePathname } from 'next/navigation';
import { Button } from '@chakra-ui/react';

import usePrefixedTranslation from '@/app/hooks/usePrefixedTranslation';

interface NavigationButtonProps {
    isAuthenticated: boolean;
  } 

const NavigationButton: React.FC<NavigationButtonProps> = ({isAuthenticated}) => {
    // const router = useRouter();
    const pathname = usePathname();
    const { t } = usePrefixedTranslation("Components.NavigationButton")


    if (!isAuthenticated) return null; // Hide button if not authenticated
  
    const isDashboardPage = pathname === '/dashboard';
    const buttonLabel = isDashboardPage ? t("toMainPageLabel") : t("toDashboardLabel");
    const buttonHref = isDashboardPage ? '/' : '/dashboard';
  
    return (
      <Link href={buttonHref} passHref>
        <Button colorScheme="teal" variant="solid">
          {buttonLabel}
        </Button>
      </Link>
    );
}

export default NavigationButton