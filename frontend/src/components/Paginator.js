import { Pagination } from "react-bootstrap";

export default function Paginator({page_info, onPageSelected}) {
    /*
     page_info: {
        current_page_num: 1,
        pages: [1,2,3]
     }
    */

    function getPageArray(currentPage, maxPage, sideElems) {
        let pArray = [];
        const startIndex = Math.max(currentPage - sideElems, 1);
        const endIndex = Math.min(currentPage + sideElems, maxPage);
        for(let i = startIndex; i <= endIndex; i++) {
            pArray.push(i);
        }
        return pArray;
    }

    function handlePrev() {
        onPageSelected(page_info.current_page_num-1)
    }

    function handleNext() {
        onPageSelected(page_info.current_page_num+1)
    }

    if(page_info) {
        return (
            <Pagination>
                { page_info.current_page_num > 1 ? <Pagination.Item onClick={handlePrev}>Prev</Pagination.Item> : <></> }
                { getPageArray(page_info.current_page_num, page_info.pages, 2).map(pNum => (
                    <Pagination.Item key={pNum} onClick={()=> onPageSelected ? onPageSelected(pNum) : undefined} active={pNum === page_info.current_page_num}>{pNum}</Pagination.Item>
                ))}
                { page_info.current_page_num < page_info.pages ? <Pagination.Item onClick={handleNext}>Next</Pagination.Item> : <></> }
            </Pagination>
        );
    } else {
        return (
            <Pagination>
                <Pagination.Item key={1} active={true}>1</Pagination.Item>
            </Pagination>
        );
    }

   
}