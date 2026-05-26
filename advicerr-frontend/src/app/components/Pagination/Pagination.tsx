import React from 'react'


type PaginationProps = {
    currentPage: number;
    totalPages: number;
    onPageChange: (page: number) => void;
  };
  
  const Pagination = ({ currentPage, totalPages, onPageChange }: PaginationProps) => {
    const handlePrev = () => {
      if (currentPage > 1) onPageChange(currentPage - 1);
    };
  
    const handleNext = () => {
      if (currentPage < totalPages) onPageChange(currentPage + 1);
    };
  
    // Ensure totalPages is a valid positive number
    if (!totalPages || totalPages <= 0) {
      console.error("Invalid totalPages value:", totalPages);
      return null; // Don't render pagination if totalPages is invalid
    }
  
    return (
      <ol className="flex justify-center gap-1 text-xs font-medium">
        <li>
          <button
            onClick={handlePrev}
            className={`inline-flex size-8 items-center justify-center rounded border border-gray-100 bg-white text-gray-900 ${
              currentPage === 1 ? "cursor-not-allowed opacity-50" : ""
            }`}
            disabled={currentPage === 1}
          >
            <span className="sr-only">Prev Page</span>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-3 w-3"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        </li>
  
        {[...Array(totalPages)].map((_, i) => (
          <li key={i}>
            <button
              onClick={() => onPageChange(i + 1)}
              className={`block size-8 rounded border ${
                currentPage === i + 1
                  ? "border-teal-400 bg-teal-600 text-white"
                  : "border-gray-100 bg-white text-gray-900"
              } text-center leading-8`}
            >
              {i + 1}
            </button>
          </li>
        ))}
        <li>
        <button
            onClick={handleNext}
            className={`inline-flex size-8 items-center justify-center rounded border border-gray-100 bg-white text-gray-900 ${
              currentPage === totalPages ? "cursor-not-allowed opacity-50" : ""
            }`}
            disabled={currentPage === totalPages}
          >
            {/* <a
            href="#"
            className="inline-flex size-8 items-center justify-center rounded border border-gray-100 bg-white text-gray-900 rtl:rotate-180"
            > */}
                <span className="sr-only">Next Page</span>
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-3 w-3"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                >
                    <path
                    fillRule="evenodd"
                    d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                    clipRule="evenodd"
                    />
                </svg>
            {/* </a> */}
            </button>
        </li>
      </ol>
    );
  };

export default Pagination