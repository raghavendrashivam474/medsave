# MedSave Frontend Implementation Guide

## Purpose

This document serves as the implementation guide for the MedSave frontend.

Its purpose is to establish a shared understanding of the product vision, implementation expectations, engineering constraints, and functional requirements so that the frontend remains aligned with the overall product architecture throughout development.

This is **not** a pixel-perfect design specification.

Instead, it defines **what the product should accomplish**, **which requirements are mandatory**, and **where implementation decisions are intentionally left open for creativity**.

The goal is to build a frontend that is intuitive, maintainable, reusable, and ready for seamless backend integration.

The current frontend should be treated as a proof of concept rather than the final implementation. Contributors are encouraged to use it as a reference, not as a design that must be replicated.

---

## What is MedSave?

MedSave is a platform that helps users quickly find medicines available in nearby pharmacies.

Instead of visiting multiple stores physically, a user should be able to search for a medicine, compare nearby pharmacies, check availability and pricing, and navigate to the selected pharmacy with minimum effort.

Our goal isn't just to build another medicine search website—we want to make the process of finding medicines simple, reliable and fast.

---

## Where the project currently stands

At the moment, the backend already has:

- Flask backend
- PostgreSQL database
- ETL pipeline
- Medicine dataset
- Basic search prototype

The frontend currently exists only as a simple proof of concept built using HTML, CSS and JavaScript.

You're not expected to continue that design.

---

## What the final product should feel like

A user should ideally experience something like this:

Search a medicine

↓

See matching medicines

↓

Compare nearby pharmacies

↓

Check stock, distance and price

↓

Choose the most suitable pharmacy

↓

Navigate there

Everything in the interface should help make this journey simple and intuitive.

---

## Things that are non-negotiable

These are the core features that MedSave should eventually support.

- Medicine Search
- Search Suggestions
- Search Results
- Medicine Details
- Store Details
- Nearby Pharmacy Listing
- Store Comparison
- Map / Navigation Integration
- Proper Loading States
- Empty States
- Error Handling
- Responsive Design

How these are presented is completely open to your creativity, but these capabilities should exist.

---

## While designing, please keep these things in mind

The backend will eventually provide data through APIs.

So instead of designing around hardcoded data, try to think of the interface as something that will eventually receive real information from the backend.

Some examples of information you'll receive include:

For medicines:

- Name
- Manufacturer
- Generic Name
- Price
- Availability

For pharmacies:

- Name
- Address
- Contact
- Distance
- Stock Availability

The exact structure may change slightly, but these are the main entities you'll be working with.

---

## What we're hoping the interface feels like

Rather than focusing on making it flashy, we'd love the interface to feel:

- Simple
- Professional
- Trustworthy
- Fast
- Easy to understand
- Comfortable to use

Someone opening MedSave for the first time should immediately know what to do.

---

## Where you have complete creative freedom

This is the fun part.

Feel free to explore and improve things like:

- Overall layout
- Navigation style
- Component design
- Cards
- Icons
- Color palette
- Typography
- Animations
- Micro-interactions
- Empty states
- Loading experience

If you think something can be made better, please do it.

We're not looking for someone to replicate a design—we'd love you to contribute your own ideas.

---

## A few engineering considerations

To make future integration easier, it would be great if:

- Components are reusable.
- The layout is responsive.
- The code remains modular.
- Similar UI isn't duplicated unnecessarily.
- Future API integration can happen with minimal changes.

These aren't restrictions—they're just things that will help us later.

---

## Things that are not part of the current scope

For now, don't worry about:

- Authentication
- User accounts
- Admin dashboard
- Payments
- Notifications
- AI assistant
- Analytics

Right now, we're focused on making the medicine discovery experience really solid.

---

## Finally...

This document tells you **what** we're trying to build, not **how** you should build it.

If you have an idea that improves the experience while keeping the core functionality intact, we'd genuinely love to see it.

The goal is for the frontend and backend to grow together so that when they're finally connected, they feel like parts of the same product instead of two separate projects.

Looking forward to seeing your ideas. 😊