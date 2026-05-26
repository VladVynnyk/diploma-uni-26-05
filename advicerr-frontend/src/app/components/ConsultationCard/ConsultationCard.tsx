"use client"
import React from 'react'
import { Card, CardHeader, CardBody, CardFooter, Stack, Text, Button, Heading, Image, Divider} from '@chakra-ui/react'

type Props = {}

const ConsultationCard = (props: Props) => {
  return (
    <div>
        <Card
          direction={{ base: 'column', sm: 'row' }}
          overflow='hidden'
          variant='elevated'
          size="sm"
          w="75%"
          mx="auto"
          mb="4"
        >
          <Image
            objectFit='cover'
            maxW={{ base: '100%', sm: '200px' }}
            src='https://images.unsplash.com/photo-1667489022797-ab608913feeb?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxlZGl0b3JpYWwtZmVlZHw5fHx8ZW58MHx8fHw%3D&auto=format&fit=crop&w=800&q=60'
            alt='Caffe Latte'
          />

          <Stack>
            <CardBody>
              <Heading size='md'>Title of consultation</Heading>

              <Text py='2'>
              Lorem ipsum dolor sit amet consectetur, adipisicing elit. Laborum, a qui. Dignissimos, veniam! Tempore ea molestiae adipisci, tempora quam possimus.
              </Text>
            </CardBody>

            <CardFooter>
              <Text py='2' mr="2">Score: 5</Text>
              <Divider orientation='vertical'/>
              <Text py='2' mr="2" ml="2">Price: 5</Text>
              <Button variant='solid' colorScheme='teal'>
                Buy Latte
              </Button>
            </CardFooter>
          </Stack>
        </Card>
    </div>
  )
}

export default ConsultationCard