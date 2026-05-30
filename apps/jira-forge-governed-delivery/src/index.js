import Resolver from '@forge/resolver';
import { analyzeIntake, createJiraIssuesFromTickets, getIssueContext } from './resolvers';

const resolver = new Resolver();

resolver.define('analyzeIntake', analyzeIntake);
resolver.define('createJiraIssuesFromTickets', createJiraIssuesFromTickets);
resolver.define('getIssueContext', getIssueContext);

export const handler = resolver.getDefinitions();
