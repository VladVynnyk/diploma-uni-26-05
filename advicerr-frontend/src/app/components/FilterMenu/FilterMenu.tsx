import React from 'react'
import { Stack, Divider } from '@chakra-ui/react'
import FilterButton from './FilterButton'

type Props = {}

const FilterMenu = (props: Props) => {
  const filterOptions = ["Здоров'я", "Репетиторство", "Бізнес", "Фінанси"]  
  const sortingOptions = ["Дорогі спочатку", "Дешеві спочатку"]

  return (
    <div className='flex items-center gap-6 text-sm mt-2 mb-2 h-10'>
        <Stack direction="row">
            {/* <FilterButton label="Категорія" action="chooseCategory"/> */}
            <Divider orientation='vertical'/>
            {/* <FilterButton label="Сортувати" action="sort"/> */}
        </Stack>
    </div>
  )
}

export default FilterMenu