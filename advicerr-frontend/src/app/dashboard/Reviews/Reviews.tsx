import React  from 'react';
import {
  Box, Heading, useMediaQuery
} from '@chakra-ui/react';
import SingleReview from './SingleReview';
import ReviewForm from './ReviewForm';

import { TReview } from '@/app/types/ReviewTypes';

import usePrefixedTranslation from '@/app/hooks/usePrefixedTranslation'

type Props = {
  id: string,
  reviews: Array<TReview>
}


const Reviews = ({id, reviews}: Props) => {
  const { t } = usePrefixedTranslation('Pages.DashboardPage.reviews');
  const [isMobile] = useMediaQuery("(max-width: 480px)");

  return (
    <Box>
      <Heading as="h2" size="xl" mb={4}>
        {t("reviewsLabel")}
      </Heading>
      {/* <ReviewForm userForReview={reviews}/> */}
      {reviews.map((review) => (
        <SingleReview
          key={review.id}
          name={""}
          surname={""}
          description={review.description}
          score={review.rating}
          isMobile={isMobile}
        />
      ))}


      {/* <SingleReview name="Vladyslav" 
                    surname="Vynnyk" 
                    description="That's really cool consultant." 
                    score={4.1} 
                    isMobile={isMobile}/> */}
    </Box>
  );
}

export default Reviews
