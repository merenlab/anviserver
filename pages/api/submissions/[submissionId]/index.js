import { findSubmissionById } from '@/api-lib/db';
import { getMongoDb } from '@/api-lib/mongodb';
import { ncOpts } from '@/api-lib/nc';
import nc from 'next-connect';

const handler = nc(ncOpts);

handler.get(async (req, res) => {
  const db = await getMongoDb();

  const submission = await findSubmissionById(db, req.query.submissionId);

  if (!submission) {
    return res
      .status(404)
      .json({ error: { message: 'Submission is not found.' } });
  }
});

export default handler;
