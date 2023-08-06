import * as express from 'express';

const router = express.Router();

let ID = 0;

router.get('/', async (request, response) => {
    response.json(ID);
    ID += 1;
});

export default router;
