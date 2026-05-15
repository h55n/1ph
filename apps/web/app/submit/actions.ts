'use server'

import { prisma } from '@/lib/db'

export async function submitHackathon(formData: FormData) {
  const orgName = formData.get('Organizer Name') as string
  const title = formData.get('Hackathon Title') as string
  const applyUrl = formData.get('Apply URL') as string
  const email = formData.get('Email') as string
  const notes = formData.get('Additional Notes') as string

  if (!orgName || !title || !applyUrl || !email) {
    return { error: 'Missing required fields' }
  }

  try {
    await prisma.organizerSubmission.create({
      data: {
        submittedBy: email,
        orgName,
        orgWebsite: '', // not collected in the simple form, but required by schema, we can put empty string or extract domain
        hackathonTitle: title,
        applyUrl,
        rawFormData: { email, notes },
        status: 'PENDING'
      }
    })
    return { success: true }
  } catch (error) {
    console.error('Failed to submit hackathon:', error)
    return { error: 'Failed to submit hackathon. Please try again later.' }
  }
}
